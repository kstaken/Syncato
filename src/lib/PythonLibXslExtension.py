#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.

import sys
import libxml2

from Framework import Framework
import WeblogUtil


class Callable:
    def __init__(self, anycallable):
        self.__call__ = anycallable

class PythonLibXslExtension:
 
    def __init__(self):
        pass
        
    def __del__(self):
        pass
    
    def _getDatabase(self, sysConfig):
        # Get the database configuration
        config = libxml2.xmlNode(_obj=sysConfig[0])

        return Framework().getSite(WeblogUtil.configValue(config, "/blog/id")).db
    
    def _styleInit(style, uri):
        pass
        #sys.stderr.write("Style Init called " + uri)
        
    def _ctxtInit(ctxt, uri):
        pass
        #sys.stderr.write("CTx Init called")
        
    def _styleShutdown(style, uri, data):
        pass
        #sys.stderr.write("style shutdown called")
        
    def _ctxtShutdown(ctxt, uri, data):        
        pass
        #sys.stderr.write("CTx shutdown called")
        
    # This is necessary to simulate the existence of class methods.
    _styleInit = Callable(_styleInit)
    _ctxtInit = Callable(_ctxtInit)
    _styleShutdown = Callable(_styleShutdown)
    _ctxtShutdown = Callable(_ctxtShutdown)