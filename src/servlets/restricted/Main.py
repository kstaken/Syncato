#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.

from WebKit.HTTPServlet import HTTPServlet
import traceback, sys
from threading import RLock

import Framework

class Main(HTTPServlet):
    registerShutdown = 1
    
    def __init__(self):
        HTTPServlet.__init__(self)
        
        self.mutex = RLock()
             
    def awake(self, transaction):
        # Register our shutdown handler if it hasn't already been done. This is to
        # make sure the databases are properly closed when the system is shutdown.
        self.mutex.acquire()
        try:        
            if (Main.registerShutdown == 1):
                transaction.application().addShutDownHandler(Framework.Framework().shutdown)
                Main.registerShutdown = 0
        finally:
            self.mutex.release()
            
    def respondToGet(self, transaction):
        self.process('get', transaction)
        
    def respondToPost(self, transaction):        
        self.process('post', transaction)
                        
    def respondToDelete(self, transaction):
        self.process('delete', transaction)
        
    def respondToPut(self, transaction):
        self.process('put', transaction)
        
    def process(self, method, transaction):
        request = transaction.request()
        response = transaction.response()        
        pathInfo = request.extraURLPath()

        Framework.Framework().getRouter().processRequest(method, pathInfo, request, response)
