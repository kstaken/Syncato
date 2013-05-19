# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.
#  
# $Id: XMLFragment.py,v 1.1 2003/12/15 14:57:48 kstaken Exp $

# TODO - root elements are apparently not getting set to the proper values when
# creating a document from scratch

import libxml2
        
def registerNamespaces(namespaceNodes):
    if (XMLFragment.namespaces == None):
        XMLFragment.namespaces = {}
        
    for namespace in namespaceNodes:
        prefix = namespace.prop("prefix")
        url = namespace.content
        if (url == ""):
            del XMLFragment.namespaces[prefix]
        else:
            XMLFragment.namespaces[prefix] = url

class XMLFragment:  
    namespaces = None
    
    def __init__(self, node = None):
        self.node = node
        if (isinstance(node, str) or isinstance(node, unicode)):
            self.node = libxml2.parseDoc(node)
        elif (node == None):
            self.node = libxml2.newDoc("1.0")
        
        self.base = ""
        self._registerNamespaces()
        
    def __del__(self):        
        if (self.node and isinstance(self.node, libxml2.xmlDoc)):
            #print "freeing the document"
            self.node.freeDoc() 
            self.context.xpathFreeContext()
        
    def setBase(self, xpathBase):
        if (not(xpathBase.endswith("/"))):
            xpathBase = xpathBase + "/"
        self.base = xpathBase
     
    def clearBase(self):
        self.base = ""
       
    def _applyBase(self, xpath):
        if (not(xpath.startswith("/"))):
            return self.base + xpath
        return xpath
        
    def get(self, xpath):
        """
        Returns the complete result set from an XPath query wrapped as 
        XMLFragment objects
        """
        xpath = self._applyBase(xpath)
        results = self.context.xpathEval(xpath)
        finalResults = []
        for result in results:
            finalResults.append(XMLFragment(result))
            
        return finalResults

    def getSingle(self, xpath):
        """
        Returns the first node from an XPath query.
        """
        xpath = self._applyBase(xpath)
        results = self.context.xpathEval(xpath)
        if (len(results) > 0):
            return XMLFragment(results[0])
        
        return None
        
    def getValue(self, xpath, default=""):
        """
        Returns the content of the first node from an XPath query.
        """
        xpath = self._applyBase(xpath)
        results = self.context.xpathEval(xpath)
        if (len(results) > 0):
            return results[0].content
        
        return default
    
    def _registerNamespaces(self, namespaceMap = {}):        
        self.context = self.node.doc.xpathNewContext()
        self.context.setContextNode(self.node)
        if (XMLFragment.namespaces != None):
            for prefix in XMLFragment.namespaces:
                #print "Registering %s as %s" % (prefix, XMLFragment.namespaces[prefix])
                self.context.xpathRegisterNs(prefix, XMLFragment.namespaces[prefix])        
        
    def addNode(self, path, content = None, markup = 0, createBase = 1):
        print path
        results = self._executeQuery(path)
        
        # If we didn't get any results we need to create the tree.
        if (len(results) == 0):
            index = path.rfind("/")
            
            # We're handling the root node            
            if (index == 0):
                # See if the root should be created within a namespace
                nodeName = path[index + 1:]
                nameNoPrefix = nodeName
                nsName = nodeName.split(":")
                if (len(nsName) > 1):               
                    nameNoPrefix = nsName[1]           
               
                root = self.node.newChild(None, nameNoPrefix, content)
                (namespace, nodeName) = self._getNamespace(root, nodeName)
                root.setNs(namespace)
                self.base = "/" + nodeName + "/"
            # otherwise we need to remove a step and try higher
            else:
                self.addNode(path[:index], None, markup, 0)
                # Now the rest of the path should exist so we can add the new 
                # child
                self._setValue(path, index, content, markup)
        else:
            if (createBase == 1):
                index = path.rfind("/")
                self._setValue(path, index, content, markup)
                
    def updateNode(self, path, content = "", markup = 0):
        results = self._executeQuery(path)
        
        # If the node isn't found we need to add it
        if (len(results) == 0):
            self.addNode(path, content, markup)
        # Otherwise it's an update.
        else:
            for result in results:                
                if (markup == 1):
                    self._addMarkup(None, "", result, content, 1)                    
                else:
                    if (isinstance(content, str) or content == None):
                        result.setContent(content)
                    else:
                        # Remove all the existing children of the node
                        self._freeChildren(result)
                        
                        result.addChild(content)
    
    def removeNode(self, path):
        results = self._executeQuery(path)
        
        for result in results:
            result.unlinkNode()
            result.freeNode()
            
    def insertNodeBefore(self, path, nodeName, content=None, markup=0):
        results = self._executeQuery(path)
        
        for result in results:
            node = self._processNode(result, nodeName, content, markup)            
            result.addPrevSibling(node)
                        
    def insertNodeAfter(self, path, nodeName, content=None, markup=0):
        results = self._executeQuery(path)
            
        for result in results:
            node = self._processNode(result, nodeName, content, markup)   
            result.addNextSibling(node) 
    
    def _executeQuery(self, path):
        self._applyBase(path)
        try:
            # if there's no root this throws an exception and removes some warnings
            self.node.getRootElement()
            results = self.context.xpathEval(path)            
        except:
            results = []
        
        return results
        
    def _setValue(self, path, index, content, markup = 0):
        results = self.context.xpathEval(path[:index])
        nodeName = path[index + 1:]
        
        for result in results:
            (namespace, nodeName) = self._getNamespace(result, nodeName)
            
            if (nodeName.startswith('@')):
                result.setProp(nodeName[1:], content)
            else:                    
                # If the content is specified as being markup we need to parse 
                # it before adding it to the document.
                if (markup == 1):
                    self._addMarkup(namespace, nodeName, result, content)                    
                else:
                    # Now content can either be a string or a node
                    if (isinstance(content, str) or content == None):
                        child = self.node.newDocNode(namespace, nodeName, content)
                        result.addChild(child)
                    else:
                        # First create the container node
                        parent = self.node.newDocNode(namespace, nodeName, None)
                        result.addChild(parent)          
                        
                        # Then add the content under it
                        newNode = content.copyNode(1)
                        content.reconciliateNs(content.doc)
          
                        parent.addChild(newNode)
                        
    def _processNode(self, parent, nodeName, content, markup):
        (namespace, nodeName) = self._getNamespace(parent, nodeName)
        if (markup == 1):
            node = self.node.newDocNode(namespace, nodeName, None)
    
            # we have to wrap the content to make sure there isn't more 
            # then one root node.
            wrappedContent = "<wrap>" + content + "</wrap>"
            doc = XMLFragment(wrappedContent)
            
            # Extract the parsed original content from the wrapper and 
            # replace all the content of the node                
            children = doc.xpathEval("/wrap/node()")
            for child in children:
                child.unlinkNode()
                child.reconciliateNs(self.node)
                node.addChild(child)                                        
        else:            
            node = self.node.newDocNode(namespace, nodeName, content)
        
        return node
            
    def _getNamespace(self, parent, nodeName):        
        """
        Determines if this node should be created in a namespace and returns 
        the namespace and nodename without the prefix.
        """
        namespace = None
        nsName = nodeName.split(":")
        if (len(nsName) > 1):
            prefix = nsName[0]
            nodeName = nsName[1]
            # locate the namespace for the prefix, if not found it has to be 
            # created
            try:
                namespace = parent.searchNs(self.node, prefix)
            except:
                namespace = parent.newNs(self.namespaces[prefix], prefix)
        
        return [namespace, nodeName]
                    
    def _addMarkup(self, namespace, nodeName, parent, content, update = 0):
        """
        Adds or updates a child node that contains unparsed markup.
        """            
        # we have to wrap the content to make sure there isn't more 
        # then one root node.
        wrappedContent = "<wrap>" + content + "</wrap>"
        doc = XMLFragment(wrappedContent)
        
        # If we're updating we remove all the existing children of the node
        if (update == 1):
            self._freeChildren(parent)
        # Otherwise we add the node and then append the children to it    
        else:
            parent = parent.newChild(namespace, nodeName, None)
            
        # Extract the parsed original content from the wrapper and 
        # replace all the content of the node                
        results = doc.xpathEval("/wrap/node()")
        for result in results:
            result.unlinkNode()
            result.reconciliateNs(self.node)
          
            parent.addChild(result)
        
        return parent
        
    def _freeChildren(self, parent):
        child = parent.children        
        while (child != None):            
            next = child.next
            child.unlinkNode()
            child.freeNode()
            child = next

    def getDocument(self):
        return self.node
                
    def getContent(self):
        return self.node.content
    
    def setContent(self, content):
        self.node.setContent(content)
        
    def getFragment(self):
        return self.node
        
    def serialize(self):
        return self.node.serialize()
        
    def getRootElement(self):
        return self.node.doc.getRootElement()
        
    def xpathEval(self, xpath):
        return self.context.xpathEval(xpath);

    def copy(self, recursive = 1):
        doc = XMLFragment()
        
        node = self.node.docCopyNode(doc.node.doc, recursive)
        
        node.docSetRootElement(doc.node.doc)
        return doc
    
    def newDocText(self, content):
        return self.node.newDocText(content)
        
    def __len__(self):
        return 1

    def __getitem__(self, key):
        key = self._applyBase(key)
        return self.getValue(key)
        
    def __setitem__(self, key, value):
        key = self._applyBase(key)
        self.updateNode(key, value)

    def __delitem__(self, key):
        key = self._applyBase(key)
        self.removeNode(key)

    def __iter__(self):
        return ""
        
    def __str__(self):
        return self.node.serialize()