#!/usr/local/bin/python
#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.
#
# $Id: Weblog.py,v 1.13 2004/04/15 09:29:05 kstaken Exp $
import os, sys

import Framework

class Component:
    def __init__(self, name, location):        
        self.name = name
        self.location = location + name
        self.frameworkLocation = Framework.Framework().getBasePath() + "/src/components/" + name
        print "Creating component "  + name
                
    def getController(self, name):
        # Check the specified locations
        controller = self.checkLocation(self.location, name)
        if (controller == None and self.location != self.frameworkLocation):
            controller = self.checkLocation(self.frameworkLocation, name)
            
        # if not found and the location is different, then check within the framework
        return controller
    
    
    def checkLocation(self, location, name):
        # Save off the current path so we can restore it later
        oldSysPath = sys.path
        try:
            # Add the location for the module to the beginning of the search path    
            sys.path.insert(0, location + "/controller/")
        
            path = location + "/controller/" + name.capitalize() + ".py"
            # If the path exists, dynamically load the module and instantiate the class
            if (os.path.exists(path)):
                module = __import__(name.capitalize(), globals(), locals(), name.capitalize())                
                controllerClass = vars(module)[name.capitalize()]

                return controllerClass()
        finally:
            # restore the original module search path
            sys.path = oldSysPath
        
        return None