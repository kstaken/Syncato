#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.
#  
# $Id: Comment.py,v 1.10 2003/12/15 14:57:48 kstaken Exp $

import libxml2

from BaseDatabase import NotFoundError

from DocumentBuilder import DocumentBuilder
from XMLFormServlet import XMLFormServlet
         
class Comment(XMLFormServlet):
    def __init__(self):
        XMLFormServlet.__init__(self)
             
    def respondToPost(self, transaction):
        self.respondToGet(transaction)
        
    def respondToGet(self, transaction):
        request = transaction.request()
        response = transaction.response()
        
        try:
            fields = request.fields()
            print fields['/comment/body#markup']
            # force blacklist constraints in case someone tries to post without
            # using the comment form.
            if (not "#blacklist#/comment/body" in fields):
                fields["#blacklist#/comment/body"] = self.weblog.configValue("/blog/blacklist-message")
                
            if (not "#blacklist#/comment/url" in fields):
                fields["#blacklist#/comment/url"] = self.weblog.configValue("/blog/blacklist-message")
            
            # We need to force this to only allow the creation of comment entries
            fields["#required#/comment"] = "This service can only post comments."
            
            update = DocumentBuilder(self.weblog, fields)
            
            # Which button was clicked on the form
            post = request.field('post', "")
            postID = request.field('/comment/@postID', "")
            
            errorText = update.getErrorText()                            
            if (errorText == ""):
                content = update.getDocument().serialize()
                
                # If the post button was clicked we should save the entry.
                if (post == "Post"):
                    self.weblog.db.addRecord(None, content)

                    self.sendRedirect(response, self.weblog.configValue("/blog/base-url") + "/" + postID + "?t=item")                   
                # Otherwise we should preview it.
                else:
                    preview = self.weblog.db.runTransform(content, "comment-preview", "")
                    self.sendResponseText(response, preview)                
                    return
            # We treat an error like a preview, but include the error text.        
            else:
                self.sendErrorText(response, update, errorText, "comment-preview")
                
        except NotFoundError:
            response.setStatus(404, 'Not Found')
            response.write("The post being commented on could not be located.")
            
