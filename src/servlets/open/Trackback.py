#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.
#  
# $Id: Trackback.py,v 1.5 2003/12/15 14:57:48 kstaken Exp $

import libxml2

from BaseDatabase import NotFoundError

from DocumentBuilder import DocumentBuilder
from XMLFormServlet import XMLFormServlet
from XMLFragment import XMLFragment
         
class Trackback(XMLFormServlet):
    """
    Implements the Movabletype Trackback mechanism for tracking remote comments
    on posts. Described here http://www.movabletype.org/docs/mttrackback.html
    """
    def __init__(self):
        XMLFormServlet.__init__(self)
    
    def respondToGet(self, transaction):
        # TODO: handle the __mode=rss flag to return a list of trackbacks as RSS
        
        # TODO: handling trackback via GET is supposed to be deprecated.
        self.respondToPost( transaction)
            
    def respondToPost(self, transaction):
        request = transaction.request()
        response = transaction.response()
        
        # The post the trackback applies to.
        postID = request.extraURLPath().split('/')[1]        
        try:
            spec = {
                '/trackback/@postID': postID,
                '/trackback/title': request.field('title', ""),
                '/trackback/url': request.field('url', ""),
                '#required#/trackback/url': 'The URL for the linking entry is required',
                '#blacklist#/trackback/url': self.weblog.configValue("/blog/blacklist-message"),
                
                '/trackback/excerpt': request.field('excerpt', ""),
                '#blacklist#/trackback/excerpt': self.weblog.configValue("/blog/blacklist-message"),
                '/trackback/blog_name': request.field('blog_name', "")                
            }
            update = DocumentBuilder(self.weblog, spec)
            
            errorText = update.getErrorText()                            
            if (errorText == ""):
                content = update.getDocument().serialize()
                
                self.weblog.db.addRecord(None, content)
                                           
                doc = XMLFragment() 
                doc.addNode("/response/error", "0")
                
                self.sendResponseText(response, doc.serialize())      
            else:
                doc = XMLFragment() 
                doc.addNode("/response/error", "1")
                doc.addNode("/response/message", errorText)
                
                self.sendResponseText(response, doc.serialize())
                
        except NotFoundError:
            response.setStatus(404, 'Not Found')
            response.write("The post being commented on could not be located.")
            
