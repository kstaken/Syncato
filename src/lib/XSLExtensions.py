#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.

import libxslt

import DbXslExtension
import WeblogXslExtension

def registerExtensions():
    libxslt.registerExtensionClass("http://www.xmldatabases.org/weblog", WeblogXslExtension.WeblogXslExtension)
    libxslt.registerExtensionClass("http://www.xmldatabases.org/dbxsl", DbXslExtension.DbXslExtension)
        
   