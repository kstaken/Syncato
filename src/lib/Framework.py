#!/usr/local/bin/python
#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.
#
# $Id: Weblog.py,v 1.13 2004/04/15 09:29:05 kstaken Exp $
import os
import libxml2

from Router import Router
from Component import Component
from XMLFragment import XMLFragment
from Site import Site

def Framework():
    if (_Framework.theInstance == None):
        _Framework.theInstance = _Framework()
    
    return _Framework.theInstance
            
class _Framework:
    theInstance = None
    
    def __init__(self):        
        self.basePath = ".."
        sitesConfig = XMLFragment(libxml2.parseFile(self.basePath + "/sites.xml"))

        results = sitesConfig.get("/sites/site")
        self.siteList = {}
        # Build up the list of sites for this instance
        for result in results:
            print "Registering site " + result["@url-base"]
            self.siteList[result["@url-base"]] = Site(result["@site-base"])

    def getBasePath(self):
        return self.basePath
        
    def getSite(self, name):
        return self.siteList[name]
    
    def getRouter(self):
        return Router()
        
    def getComponent(self, component):
        if (os.path.isdir(self.basePath + "/src/components/" + component)):
            return Component(component, self.basePath + "/src/components/")

        return None
        
    def shutdown(self):
        print "Starting shut down"
        for site in self.siteList:
            print "Shuting down " + site
            self.siteList[site].getDatabase().shutdown
