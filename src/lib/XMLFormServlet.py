#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.
#  
# $Id: XMLFormServlet.py,v 1.6 2003/12/15 14:57:48 kstaken Exp $

from WebKit.HTTPServlet import HTTPServlet
import traceback, sys

import libxml2

from BaseDatabase import NotFoundError

from Weblog import Weblog
         
class XMLFormServlet(HTTPServlet):    
    def __init__(self):
        HTTPServlet.__init__(self)
        self.weblog = Weblog("../config")        
                      
    def sendRedirect(self, response, location):
        response.setStatus(303, 'See Other')                
        response.setHeader("Location", location)
        
    def sendErrorText(self, response, update, errorText, style):
        errorDoc = libxml2.parseDoc("<error-text>" + errorText + "</error-text>")
        try:
            doc = update.getDocument().getDocument()
            doc.getRootElement().addChild(errorDoc.getRootElement())
        except libxml2.treeError:
            doc = update.getDocument().getDocument()
            doc.addChild(errorDoc.getRootElement())
            
        content = doc.serialize()                                
        error = self.weblog.db.runTransform(content, style, "")
        self.sendResponseText(response, error)
                   
    def sendResponseText(self, response, text):
        response.setStatus(200, "OK")
        response.setHeader('Content-type', "text/html")
        response.setHeader('Content-length', str(len(text)))
        response.write(text)