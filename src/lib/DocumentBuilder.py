#!/usr/local/bin/python
#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.
#  
# $Id: DocumentBuilder.py,v 1.8 2003/12/15 14:57:48 kstaken Exp $


from string import replace

import libxml2

import Weblog
import XMLFragment

WELL_FORMED_ERROR = """
Your post can not be parsed as well-formed XML. This means that your post contains
markup elements that are not correct. This probably means you have unclosed 
HTML tags. A common example would be typing &lt;br> when you should type &lt;br/>. 
"""

def encode(data):
    """
    Attempts to clean up submitted data. Can't do too much since we want to 
    allow XML content to be posted, but we can at least cleanup unescaped &.
    
    In reality this may not be such a great idea.
    """
    
    if (isinstance(data, str)):
        # replace any existing entities temporarily
        data = replace(data, '&amp;', '::amp::')
        data = replace(data, '&lt;', '::lt::')
        data = replace(data, '&gt;', '::gt::')
        data = replace(data, '&quot;', '::quot::')
        data = replace(data, '&apos;', '::apos::')
        
        # Replace the problem characters
        data = replace(data, '&', '&amp;')
        data = replace(data, '< ', '&lt; ')
        #data = replace(data, '>', '&gt;')
        #data = replace(data, '"', '&quot;')
        #data = replace(data, "'", '&apos;')
        
        # We also try to be friendly to blank lines
        #data = replace(data, '\n\n', '<p/>')
        
        # Restore the original entities.
        data = replace(data, '::amp::', '&amp;')
        data = replace(data, '::lt::', '&lt;')
        data = replace(data, '::gt::', '&gt;')
        data = replace(data, '::quot::', '&quot;')
        data = replace(data, '::apos::', '&apos;')
    
    return data
    
class DocumentBuilder:
    def __init__(self, weblog, spec):
        self.spec = spec
        self.weblog = weblog
        
        self.errorText = ""
        
        # See if we're updating an existing entry.
        self.update = 0
        self.postID = -1
        if (("@id" in spec) and (spec["@id"] != "")):
            self.postID = spec["@id"]
            self.doc = XMLFragment.XMLFragment(self.weblog.db.getRecord(None, self.postID))
            self.update = 1        
        else:    
            self.doc = XMLFragment.XMLFragment()
            
        self._buildDocument()
        self._validateDocument()

        
    def _buildDocument(self):
        """
        Constructs the initial document without applying any constraints.
        """
        
        for field in self.spec:
            if field.startswith('/'):
                # Look for processing hints to adjust how the document is to be 
                # constructed.
                elements = field.split("#")
                
                # The node path is the first element, the rest define 
                # processing hints
                nodePath = elements[0]
                hints = elements[1:]
                
                # See if this field should be parsed as markup when adding it
                # to the document.
                markup = 0
                if ("markup" in hints):  
                    markup = 1
                
                fieldContent = encode(self.spec[field]) 
                try:                                        
                    if (self.update == 0):
                        # We only create the node if the field has content.
                        if (fieldContent != ""):
                            # We're creating a new document
                            if (isinstance(fieldContent, str)):                    
                                self.doc.addNode(nodePath, fieldContent, markup)    
                            else:
                                for value in fieldContent:
                                    self.doc.addNode(nodePath, encode(value), markup) 
                    else:
                        # We're updating an existing document
                        if (isinstance(fieldContent, str)):     
                            self.doc.updateNode(nodePath, fieldContent, markup)    
                        else:
                            # For multiple values we first remove all the entries 
                            # at the path.
                            self.doc.removeNode(nodePath)
                            
                            # Then add new ones for the submitted entry.
                            for value in fieldContent:
                                self.doc.addNode(nodePath, encode(value), markup)
                except:
                    if (self.update == 0):
                        self.doc.addNode(nodePath, fieldContent, 0)
                    else:
                        self.doc.updateNode(nodePath, fieldContent, 0)
                    self.errorText += WELL_FORMED_ERROR + "<br/>"

        # Cleanup the field names to remove processing hints for use in 
        # validation.
        newSpec = {}
        for field in self.spec:
            if field.startswith('/'):
                elements = field.split("#")
                nodePath = elements[0]

                newSpec[nodePath] = self.spec[field]
            else:
                newSpec[field] = self.spec[field]
        self.spec = newSpec
                
    def _validateDocument(self):
        """
        Document validation makes sure the document created matches a minimal
        specification. This does not restrict the structure of the document like
        a traditional XML schema language.
        """
        for field in self.spec:
            if field.startswith('#'):
                # Facets define additional criteria applied to the node 
                # modifications
                facets = field.split("#")
                
                # For validation the node path is the last element and all 
                # constraints come before it.
                nodePath = facets[-1]
                constraints = facets[:-1]
                
                # A required restraint means that the field should have a value
                if ("required" in constraints):
                    node = self.doc.getDocument().xpathEval(nodePath)
                    if (not node or node[0].content.strip() == ""):
                        self.errorText += self.spec[field] + "<br/>"               
                
                # A marker is used on multi-value entries like checkboxes to 
                # handle the case where all the values are unselected and 
                # the document in the database already has values set.
                if ("marker" in constraints):
                    # We check to see if the marked field exists with real 
                    # values. If it doesn't then we need to remove any existing
                    # values for the field
                    if (not nodePath in self.spec):
                        self.doc.removeNode(nodePath)
                
                # A blacklist constraint checks all the URLs in the item against 
                # a list of blacklisted URLs to see if the item should be 
                # allowed or not.
                if (self.weblog.configValue("/blog/use-blacklist") == "yes"):
                    if ("blacklist" in constraints):
                        self._checkBlacklist(self.spec[nodePath], self.spec[field])
                
    def _checkBlacklist(self, content, message):
        # Check for a direct string, we're just interested in the hostname so 
        # we need to clean it up.
        if (self._checkURL(content, message) == 0):
            # No match on a plain string so we need to try parsing as XML to 
            # see there are any embedded URLs
            try:
                contentDoc = XMLFragment("<wrap>" + content + "</wrap>")
                urls = contentDoc.xpathEval("//@href")
                for url in urls:
                    self._checkURL(url.content, message)
            except:
                # if this fails then we don't worry because it will get rejected
                # anyway.
                pass
        
    def _checkURL(self, url, message):
        """
        Cleans up a URL and then checks it against the blacklist to see if it
        should be denied.
        """
        url = url.strip()
        
        url = replace(url, "'", '"')
        url = replace(url, "http://", "")
        url = url.split("/")[0]
        query = "/blacklist[url='" + url + "']"
        
        result = self.weblog.db.xpathQuery(None, query)
        
        doc = libxml2.parseDoc(result)
        try:
            results = doc.xpathEval("/results/blacklist")
            if (len(results) > 0):
                self.errorText += message % url  + "<br/>"
                doc.freeDoc()
                return 1
        except Error, e:
            print e
            
        doc.freeDoc()
        return 0

    def getPostID(self):
        return self.postID
        
    def getDocument(self):
        return self.doc
        
    def serialize(self):
        return self.doc.serialize()
        
    def getRootElement(self):
        return self.doc.getRootElement()
        
    def xpathEval(self, xpath):
        return self.doc.xpathEval(xpath);
        
    def getErrorText(self):
        return self.errorText
        
    def isUpdate(self):
        return self.update

        
# Unit tests for this module.
       
import unittest, os
        
testEntry = """<item>
    <title>Test Post 1</title>
    <description>Just a simple <b>post</b> to get started.</description>
    <category>XML</category>
    <category>Java</category>
</item>
"""
        
class TestXMLFragment(unittest.TestCase):
                    
    def testNewDocument(self):
        spec = {
            '/item/title': 'Test Post 1'            
        }
                
        weblog = Weblog.Weblog("../config")
        doc = DocumentBuilder(weblog, spec)
         
        self.assertEqual(doc.getDocument().serialize(), '<?xml version="1.0"?>\n<item><title>Test Post 1</title></item>\n')
        
        # test creating a multi-value element
        spec = {
            '/item/category': ['XML', 'Java'],
            '#marker#/item/category': '#marker'
        }
        
        doc = DocumentBuilder(weblog, spec)
        self.assertEqual(doc.getDocument().serialize(), '<?xml version="1.0"?>\n<item><category>XML</category><category>Java</category></item>\n')
        
        # test a required assertion for title     
        spec = {
            '#required#/item/title': 'Title is required',
            '/item/category': ['XML', 'Java'],
        }
        
        doc = DocumentBuilder(weblog, spec)
        self.assertEqual(doc.getErrorText(), 'Title is required<br/>')
        
        # Test the markup processing hint
        spec = {          
            '/item/description#markup': 'Just a simple <b>post</b> to get started.'            
        }
        
        doc = DocumentBuilder(weblog, spec)
        self.assertEqual(doc.getDocument().serialize(), '<?xml version="1.0"?>\n<item><description>Just a simple <b>post</b> to get started.</description></item>\n')
        
if __name__ == '__main__':
    import sys
   # sys.path.append("scripts/lib")
    unittest.main()
    
    