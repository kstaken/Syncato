#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.

import httplib, string, re
from base64 import encodestring
from urllib import quote

import libxml2

class WeblogClient:
    
    def __init__(self, host, baseURL, username, password):
        self.conn = httplib.HTTPConnection(host)
        self.host = host
        self.baseURL = baseURL
        self.username = username
        self.password = password
        
    def getPost(self, postID):
        postID = self.cleanPostID(postID)
        
        result = self.runRequest("GET", postID)
        
        if (result.status == 200):
            data = result.read().strip()
            
            item = libxml2.parseDoc(data)
            
            result = {}
            result['title'] = item.xpathEval("/item/title")[0].content
            result['body'] = item.xpathEval("/item/description")[0].serialize()
            
            results = item.xpathEval("/item/category")
            categories = []
            for category in results:
                categories.append(category.content)
                
            result['categories'] = categories
        
            return result
        else:
            return None

    def getRawPost(self, postID):
        postID = self.cleanPostID(postID)
        
        result = self.runRequest("GET", postID)
        
        if (result.status == 200):
            data = result.read().strip()
                        
            return data
        else:
            return None
            
    def addRawPost(self, entry):
        """
        Adds a plain XML entry to the database.
        """
        result = self.runRequest("POST", self.baseURL, entry)
        
        if (result.status == 201):
            location = result.getheader("Location")
            result.read()
            return location
        else:
            return ""

    def editRawPost(self, postID, body): 
        postID = self.cleanPostID(postID)
           
        result = self.runRequest("PUT", postID, body)
                        
    def addPost(self, title, body, categories):
        """
        Adds a weblog entry to the database.
        """
        item = self.buildItem(title, body, categories)
        
        result = self.runRequest("POST", self.baseURL, item.serialize(None, 1))
        
        if (result.status == 201):
            location = result.getheader("Location")
            
            return location
        else:
            return ""

    def deletePost(self, postID):
        postID = self.cleanPostID(postID)
        
        result = self.runRequest("DELETE", postID)
        
        return result
        
    def editPost(self, postID, title, body, categories):
        postID = self.cleanPostID(postID)
        
        result = self.runRequest("GET", postID)
        itemXML = result.read().strip()
        
        item = libxml2.parseDoc(itemXML)
        
        # Update the title
        elem = item.xpathEval("/item/title")[0]        
        elem.setContent(title)
        
        # Update the description
        elem = item.xpathEval("/item/description")[0]        
        # This won't work if the content is XML
        elem.unlinkNode()
        
        bodyDoc = libxml2.parseDoc("<description>" + body + "</description>")
        item.getRootElement().addChild(bodyDoc.getRootElement())
        
        # Update the list of categories. 
        results = item.xpathEval("/item/category")
        # First we have to remove the existing categories
        for category in results:
            category.unlinkNode()
            
        # Then add the new categories
        for category in categories:
            item.getRootElement().newChild(None, "category", category.strip())
            
        result = self.runRequest("PUT", postID, item.serialize())
        
        return result
        
    def cleanPostID(self, postID):      
        stripHTTP = re.compile(r"http://.+?/", re.IGNORECASE)
        if (postID.startswith("http://")):
            postID = "/" + stripHTTP.sub("", postID)
          
        return postID
            
    def buildItem(self, title, body, categories):
        item = libxml2.newDoc("1.0")
        
        root = item.newChild(None, "item", None)
        
        root.newChild(None, "title", title)
        bodyDoc = libxml2.parseDoc("<description>" + body + "</description>")
        root.addChild(bodyDoc.getRootElement())

        for category in categories:
            root.newChild(None, "category", category.strip())
            
        return item
        
    def runRequest(self, method, url, body = None):
        token = "Basic " + encodestring(self.username + ":" + self.password).strip()
        headers = {"Content-type": "text/xml", "Authorization": token}
        
        self.conn.request(method, quote(url), body, headers)
    
        result = self.conn.getresponse()
            
        return result