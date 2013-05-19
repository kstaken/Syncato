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
from Database import Database
from Component import Component

class Site:
    def __init__(self, sitePath):        
        self.sitePath = sitePath
        print "Creating site at path "  + sitePath
        # TODO: make sure the config file actually exists
        self.config = XMLFragment(libxml2.parseFile(sitePath + "/config/config.xml"))
   
        self.db = Database(self.config)
        
    def getConfig(self):
        return self.config
        
    def getDatabase(self):
        return self.db
        
    def getComponent(self, name):
        if (os.path.isdir(self.sitePath + "/components/" + name)):
            return Component(name, self.sitePath + "/components/")

        return None
        
    def getConfigValue(self, xpath, default=""):
        results = self.config.xpathEval(xpath)
        if (len(results) > 0):
            return results[0].content
        else:
            return default
