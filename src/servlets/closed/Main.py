#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.
#  
# $Id: Main.py,v 1.6 2003/12/15 14:57:48 kstaken Exp $

from string import replace

import libxml2

from XMLFormServlet import XMLFormServlet

from DocumentBuilder import DocumentBuilder
from XMLFragment import XMLFragment

from BaseDatabase import NotFoundError

class Main(XMLFormServlet):    
    def __init__(self):
        XMLFormServlet.__init__(self)
                     
    def respondToGet(self, transaction):
        request = transaction.request()
        response = transaction.response()
        
        pathInfo = request.extraURLPath()
        
        if (pathInfo == "" or pathInfo == "/"):
            # We handle gets by just returning the basic edit page       
            content = self.weblog.db.runTransform("<dummy/>", "item/editor", "")
            self.sendResponseText(response, content)  
        elif (pathInfo.startswith("/collection")):
            # The type of collection is part of the url
            type = replace(pathInfo, "/collection/", "")
            
            collection = type + "/collection" 
            
            # Locate the collection description
            file = open(self.weblog.db.locateFile(collection, ".xml")).read()

            # Convert it to HTML
            content = self.weblog.db.runTransform(file, "admin/collection", "")
            self.sendResponseText(response, content)
                    
    def respondToPost(self, transaction):        
        request = transaction.request()
        response = transaction.response()

        entryType = request.field('type', "")
        
        fields = request.fields()
        
        try:
            entryDocument = DocumentBuilder(self.weblog, fields)
            content = entryDocument.serialize()
            
            print content
            # Convert the rest of the form into an XML form spec.
            formDocument = self._buildFormDocument(fields)
               
            errorText = ""
            try:
                # If there was a problem building the initial document we just
                # want to display an error.
                errorText = entryDocument.getErrorText()
                if (errorText != ""):
                    raise ProcessingError()
                # Otherwise we continue processing the document.
                else:        
                    # Add the entry document into the form specification.
                    formDocument.getDocument().addNode("/form/content", entryDocument.getRootElement())
                                 
                    # Hand the form spec to the action processor for this entry 
                    # type.
                    content = formDocument.serialize()
             #       print content
                    result = self.weblog.db.runTransform(content, entryType + "/action", "", "admin/action")
                        
                    print result
                    actionResult = XMLFragment(result)
                    
                    # If there were any errors in processing we send an error 
                    # to the user.
                    errors = actionResult.xpathEval("/results/error-text")
                    if (len(errors) > 0):                        
                        for error in errors:
                            errorText = error.content + "<br/>"
                            
                        raise ProcessingError()
                    # Otherwise we figure ou what button was clicked so that we 
                    # forward the user to the proper place.
                    else:
                        button = formDocument.xpathEval("/form/button/node()")[0].name
                        #print button
                        
                        style = self.getStyle(request, actionResult, "/results/action/" + button)
                        #print style
                        self.sendResponse(response, entryDocument, style)
                
            except ProcessingError, e:
                # Make sure the document actually has content and then add the 
                # error message to it.
                try:
                    root = entryDocument.getRootElement()
                    entryDocument.getDocument().addNode("/node()/error-text", errorText, 1)
                except:
                    entryDocument.getDocument().addNode("/dummy/error-text", errorText, 1)
                
                print entryDocument.serialize()
                style = self.getStyle(request, formDocument, "/form/action/error")
                
                self.sendResponse(response, entryDocument, style)
            
        except NotFoundError, e:
            doc = XMLFragment("<error-text>Document not found</error-text>")
            self.sendResponse(response, doc, "admin/error")           
        
    def _buildFormDocument(self, fields):
        updatedFields = {}
        for field in fields:
            if (not field.startswith("/") and not field.startswith("#")):
                updatedFields["/form/" + field] = fields[field]

        return DocumentBuilder(self.weblog, updatedFields)

    def getStyle(self, request, document, path, defaultStyle = "admin/error"):
        style = document.xpathEval(path)
        if (len(style) > 0):
            style = style[0].content
            if (style == "referer"):
                style = request.environ()['HTTP_REFERER']
        else:
            style = defaultStyle
            
        return style
        
    def sendResponse(self, response, document, target):
        # if the target is a URL we send a redirect
        if (target.startswith("http://")):
            self.sendRedirect(response, target)
        # Otherwise we're forwarding to a stylesheet
        else:
            content = document.serialize()
         #   print target
            print content
            result = self.weblog.db.runTransform(content, target, "")
            self.sendResponseText(response, result) 
            
class ProcessingError (Exception):
    """
    Exception that is thrown when an error occurs during processing.
    """
    pass
