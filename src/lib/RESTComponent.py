#!/usr/local/bin/python
#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.
#
# $Id: Weblog.py,v 1.13 2004/04/15 09:29:05 kstaken Exp $

import os
import libxml2

from XMLFragment import XMLFragment
from Exceptions import *

class RESTComponent:
    def get(self, context):
        result = ""
        response = context['response']
        try: 
            recordID = context['recordID']
            query = context['query']
            if (recordID != -1):
                if (query):
                    result = self.db.xpathQueryRecord(postID, query)            
                else:
                    result = self.db.getRecord(None, postID)        
            elif (query):
                result = self.db.xpathQuery(None, query)
        except NotFoundError:
            response.setStatus(404, 'Not Found')

        return result
        
    def post(self, context):
        response = context['response']
        try: 
            rawInput = request.rawInput(rewind=1)
            if (rawInput):
                content = rawInput.read()            
                postID = str(self.db.addRecord(None, content))
                
                response.setStatus(201, 'Created')
                response.setHeader("Location", self.site.getConfigValue("/blog/base-url") + "/" + postID)         
        except NotFoundError:
            response.setStatus(404, 'Not Found')
        
    def put(self, context):
        response = context['response']
        try:
            rawInput = request.rawInput(rewind=1)
            if (rawInput):                
                content = rawInput.read()                    
                self.db.updateRecord(None, context['recordID'], content)
            
                response.setStatus(205, "Reset Content")
        except NotFoundError:
            response.setStatus(404, 'Not Found')

    def delete(self, context):
        try:
            self.db.deleteRecord(None, context['recordID'])
            
            response.setStatus(200, 'OK')
        except NotFoundError:
            response.setStatus(404, 'Not Found')
        