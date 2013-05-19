#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.
#  
# $Id: WeblogXslExtension.py,v 1.9 2003/12/15 14:57:48 kstaken Exp $

import sys

import libxml2, libxslt

import textile

from PythonLibXslExtension import PythonLibXslExtension, Callable

from XMLFragment import XMLFragment
from Framework import Framework

import string, re
from string import replace

from urllib import quote    
    
class WeblogXslExtension (PythonLibXslExtension):
    instance = None

    def getConfig(self, ctx, name):
        if (not isinstance(name, str)):
            node = libxml2.xmlNode(_obj=name[0])
            name = node.content

        return Framework().getSite(name).getConfig().getDocument().xpathEval("/node()")
        
    def serialize(self, ctx, content):
        if (not isinstance(content, str)):
            result = []
            for item in content:
                node = libxml2.xmlNode(_obj=item)
            
                result.append(node.serialize())
            return "".join(result)
            
        return content
        
    def summarize(self, ctx, content, wordCount = 50):
        result = ""
        # If the content-type is XML then the tags have already been escaped. So 
        # we need to switch them back.
        summary = content
        if (len(content) != 0):
            # If we're not getting a string then it should be a node so we convert.
            if (not isinstance(content, str)):
                node = libxml2.xmlNode(_obj=content[0])
                summary = node.content
                  
            # Make the selected number of words available 
            words = summary.split(None, int(wordCount) + 1)
            
            result = " ".join(words[0:int(wordCount)])
            if (len(words) > wordCount):
                result += "..."
                
        return result
        
    def textileProcess(self, ctx, content):
        """
        An XSL-T extension function to process textile formatting included in a post.
        
        Note: this doesn't work correctly if you want to also post process the result
        as XSL.
        
        content - a single element list containing an xmlNode containing the data to style
        """
        try:
            node = libxml2.xmlNode(_obj=content[0])
            parserContext = libxslt.xpathParserContext(_obj=ctx)
            xpathContext = parserContext.context()
            
            resultContext = xpathContext.transformContext()
            
            # If this is CDATA content we want textile to treat like a pre tag
            content = replace(node.serialize(), "<![CDATA[", "<pre>")
            content = replace(content, "]]>", "</pre>")
            
            source = textile.textile(content)            
            
            source = replace(source, "<pre>", "")
            source = replace(source, "</pre>", "")
            
            return source
        except:
            sys.stderr.write("Textile processing error ")
            sys.stderr.write(source)
        return ""

    def urlencode(self, ctx, content):
        """
        Encodes special characters in URLs so that they can be used by the 
        document function.
        """
        if (isinstance(content, str)):
            return quote(content, '/:')
            
        return content
    
    def previousItem(self, ctx, sysConfig, baseURL,id):
        return self.getItem(ctx, sysConfig, baseURL, id, -1)
        
    def nextItem(self, ctx, sysConfig, baseURL,id):
        return self.getItem(ctx, sysConfig, baseURL, id, 0)
        
    def getItem(self, ctx, sysConfig, baseURL,id, index):
        try:
            db = self._getDatabase(sysConfig)
            
            if (not isinstance(id, str)):
                node = libxml2.xmlNode(_obj=id[0])
                id = node.content
            
            if (id != ""):
                if (index == 0):
                    content = db.xpathQuery(None, '/item[@id > ' + str(id) + ']')
                else:
                    content = db.xpathQuery(None, '/item[@id < ' + str(id) + ']')
                ids = libxml2.parseDoc(content).xpathEval("/results/item/@id")
                
                idList = []
                for id in ids:
                    idList.append(int(id.content))
                
                if (len(ids) > 0):
                    idList.sort()   
                
                    previousID = idList[index]
                    
                    previous = XMLFragment(db.getRecord(None, previousID))
                    title = previous.getValue("/item/title")
                                   
                    return self.itemLink(ctx, baseURL, title, previousID)
                else:
                    return ""
            else:
                return ""
        except Exception, err:
            db.log.exception("DbXslExtension: Error getting previous item")            
     
    def itemLink(self, ctx, baseURL, title, postID=""):
        """
        Encodes special characters in URLs so that they can be used by the 
        document function.
        """        
        if (isinstance(title, list) and len(title) == 0):
            title = ""
        elif (isinstance(title, list) and len(title) > 0):    
            title = libxml2.xmlNode(_obj=title[0]).content
            
        if (isinstance(baseURL, list)):    
            baseURL = libxml2.xmlNode(_obj=baseURL[0]).content
                        
        # Handle escaping of real underscores
        title = replace(title, "_", "\_")
        title = replace(title, " ", "_")
        
        if (isinstance(postID, list)):
            postID = libxml2.xmlNode(_obj=postID[0]).content
        
        title = quote("_" + title)
        
        url = "%s/%s%s.item" % (baseURL, postID, title)
            
        return url
        
    def normalizeURL(self, ctx, url):
        """
        Strips a URL down to just the host name.
        """
        
        if (isinstance(url, list)):
            node = libxml2.xmlNode(_obj=url[0])
            url = node.content
        print url
        url = url.strip()
        url = replace(url, "http://", "")
        url = url.split("/")[0]
        
        return url
        
    def _styleInit(style, uri):                  
        if (WeblogXslExtension.instance == None):
            WeblogXslExtension.instance = WeblogXslExtension()
            
        libxslt.registerExtModuleFunction("getConfig", uri, WeblogXslExtension.instance.getConfig)  
        libxslt.registerExtModuleFunction("summarize", uri, WeblogXslExtension.instance.summarize)        
        libxslt.registerExtModuleFunction("textile", uri, WeblogXslExtension.instance.textileProcess)
        libxslt.registerExtModuleFunction("serialize", uri, WeblogXslExtension.instance.serialize)
        libxslt.registerExtModuleFunction("urlencode", uri, WeblogXslExtension.instance.urlencode)
        libxslt.registerExtModuleFunction("itemlink", uri, WeblogXslExtension.instance.itemLink)
        libxslt.registerExtModuleFunction("normalizeURL", uri, WeblogXslExtension.instance.normalizeURL)
        
        libxslt.registerExtModuleFunction("previousItem", uri, WeblogXslExtension.instance.previousItem)
        libxslt.registerExtModuleFunction("nextItem", uri, WeblogXslExtension.instance.nextItem)
    _styleInit = Callable(_styleInit)
    