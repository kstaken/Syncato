#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.

from WebKit.HTTPServlet import HTTPServlet
import traceback, sys

import libxml2

from Weblog import Weblog
from XMLFragment import XMLFragment
from BaseDatabase import NotFoundError
from WeblogDirectory import WeblogDirectory


from threading import RLock

class Main(HTTPServlet):
    registerShutdown = 1
    
    def __init__(self):
        HTTPServlet.__init__(self)
        
        self.blogDirectory = WeblogDirectory("../blogs.xml")    
        self.mutex = RLock()
             
    def awake(self, transaction):
        # Register our shutdown handler if it hasn't already been done. This is to
        # make sure the databases are properly closed when the system is shutdown.
        self.mutex.acquire()
        try:        
            if (Main.registerShutdown == 1):
                transaction.application().addShutDownHandler(self.blogDirectory.shutdown)
                Main.registerShutdown = 0
        finally:
            self.mutex.release()
            
    def respondToGet(self, transaction):
        request = transaction.request()
        response = transaction.response()
        
        pathInfo = request.extraURLPath() 

        try:
            (blog, pathInfo) = self._parsePathInfo(pathInfo)
            weblog = self.blogDirectory.getBlog(blog)
        
            try:
                stylesheet = request.field('t', "")
                # Extra optional argument that can be passed to the stylesheet
                arg = request.field('a', "")
            
                # Content query that can be applied as a final step to extract
                # something from the rendered content
                contentQuery = request.field('c', "")
            
                result = weblog.handleRequest(pathInfo, stylesheet, arg, contentQuery)
            
                # Determine the content-type for the result
                if (result.startswith("<?xml")):                             
                    contentType = "text/xml"         
                elif (result.startswith("<html")):
                    contentType = "text/html"
                else:
                    contentType = "text/plain"
                #print result
                
                response.setStatus(200, 'OK')
                response.setHeader('Content-type', contentType)
                response.setHeader('Content-length', str(len(result)))
                response.write(result)
            except NotFoundError:
                response.setStatus(404, 'Not Found')
        except KeyError, IndexError:
            response.setStatus(404, 'Weblog Not Found')
        
    def respondToPost(self, transaction):        
        rawInput = transaction.request().rawInput(rewind=1)
        request = transaction.request()
        response = transaction.response()
        
        pathInfo = request.extraURLPath()                 
        try:
            (blog, pathInfo) = self._parsePathInfo(pathInfo)
            weblog = self.blogDirectory.getBlog(blog)
        
            try: 
                if (rawInput):
                    content = rawInput.read()            
                    postID = str(weblog.db.addRecord(None, content))
                    response.setStatus(201, 'Created')
                    response.setHeader("Location", weblog.configValue("/blog/base-url") + "/" + postID)         
            except NotFoundError:
                response.setStatus(404, 'Not Found')
            #except:
                
            #    response.setStatus(500, 'Server Error')
        except KeyError, IndexError:
            response.setStatus(404, 'Weblog Not Found')
            
                
    def respondToDelete(self, transaction):
        request = transaction.request()
        pathInfo = request.extraURLPath() 
        
        response = transaction.response()
        
        try:
            (blog, pathInfo) = self._parsePathInfo(pathInfo)
            weblog = self.blogDirectory.getBlog(blog)
                
            try:
                pathInfo = pathInfo[1:]
                weblog.db.deleteRecord(None, int(pathInfo))
                response.setStatus(200, 'OK')
            except NotFoundError:
                response.setStatus(404, 'Not Found')
        except KeyError, IndexError:
            response.setStatus(404, 'Weblog Not Found')
        
    def respondToPut(self, transaction):
        request = transaction.request()
        pathInfo = request.extraURLPath() 
        pathInfo = pathInfo[1:]
        
        rawInput = transaction.request().rawInput(rewind=1)
        response = transaction.response()
        
        try:
            (blog, pathInfo) = self._parsePathInfo(pathInfo)
            weblog = self.blogDirectory.getBlog(blog)
        
            try:
                if (rawInput):
                    content = rawInput.read()                    
                    weblog.db.updateRecord(None, int(pathInfo), content)
                
                    response.setStatus(205, "Reset Content")
                else:
                    print "EMPTY REQUEST"
            except NotFoundError:
                response.setStatus(404, 'Not Found')
        except KeyError, IndexError:
            response.setStatus(404, 'Weblog Not Found')
            
    def _parsePathInfo(self, pathInfo):
        # extract the blog instance from the path Info
        pathComponents = pathInfo.split("/") 
        if (len(pathComponents) > 1):
            blog = pathComponents[1]
            pathInfo = pathInfo.replace("/" + blog, "")
            return (blog, pathInfo)    
        else:
            return(None, None)