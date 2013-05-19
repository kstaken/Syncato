#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved. 
#  
# $Id: DbXslExtension.py,v 1.5 2003/12/15 14:57:48 kstaken Exp $

import sys

import libxml2, libxslt

from PythonLibXslExtension import PythonLibXslExtension, Callable

from XMLFragment import XMLFragment

class DbXslExtension (PythonLibXslExtension):
    instance = None
    
    def __init__(self):
        self.cleanupList = []
    
    def xpathQuery(self, ctx, sysConfig, xpath):
        # Get the database configuration
        try:        
            db = self._getDatabase(sysConfig)
            
            if (not isinstance(xpath, str)):
                node = libxml2.xmlNode(_obj=xpath[0])
                xpath = node.content

            content = db.xpathQuery(None, xpath)

            # See if this looks like an XML result
            if (content.startswith("<?xml")):                                  
                doc = XMLFragment(content)
                # Extract the expected result set now that we've converted into libxml format.
                result = doc.xpathEval("/results/*")
                self.cleanupList.append(doc)
            else:
                doc = XMLFragment(libxml2.newDoc("1.0"))
                
                result = [doc.newDocText(content)]
                self.cleanupList.append(doc)
                            
            return result
        except Exception, err:
            db.log.exception("DbXslExtension: Error searching")            
 
    def deleteRecord(self, ctx, sysConfig, entryID):
        try:            
            if (not isinstance(entryID, str)):
                node = libxml2.xmlNode(_obj=entryID[0])
                entryID = node.content

            db = self._getDatabase(sysConfig)
            
            db.deleteRecord(None, entryID)

            return "success"
        except:
            db.log.exception("DbXslExtension: Error deleting")
            return "Error"

    def addRecord(self, ctx, sysConfig, entry):
        print "adding record"
        try:            
            entry = libxml2.xmlNode(_obj=entry[0])
            
            db = self._getDatabase(sysConfig)
            
            db.addRecord(None, entry.serialize())

            print "added record " + entry.serialize()
            return "success"
        except:
            db.log.exception("DbXslExtension: Error adding")
            return "Error"

    def updateRecord(self, ctx, sysConfig, entryID, entry):
        print "updating record"
        try:                        
            if (not isinstance(entryID, str)):
                node = libxml2.xmlNode(_obj=entryID[0])
                entryID = node.content

            entry = libxml2.xmlNode(_obj=entry[0])
            db = self._getDatabase(sysConfig)
            
            db.updateRecord(None, entryID, entry.serialize())
            return "success"
        except:
            db.log.exception("DbXslExtension: Error updating")
            return "Error"

    def getRecord(self, ctx, sysConfig, entryID):
        print "getting record"
        try:            
            if (not isinstance(entryID, str)):
                node = libxml2.xmlNode(_obj=entryID[0])
                entryID = node.content

            db = self._getDatabase(sysConfig)
            return db.getRecord(None, entryID)
        except Exception, err:
            db.log.exception("DbXslExtension: Error getting record")
            return "Error"
            
    def _styleInit(style, uri):        
        if (DbXslExtension.instance == None):
            DbXslExtension.instance = DbXslExtension()
                
        libxslt.registerExtModuleFunction("xpathQuery", uri, DbXslExtension.instance.xpathQuery)
        libxslt.registerExtModuleFunction("deleteRecord", uri, DbXslExtension.instance.deleteRecord)
        libxslt.registerExtModuleFunction("addRecord", uri, DbXslExtension.instance.addRecord)
        libxslt.registerExtModuleFunction("updateRecord", uri, DbXslExtension.instance.updateRecord)
        libxslt.registerExtModuleFunction("getRecord", uri, DbXslExtension.instance.getRecord)
    _styleInit = Callable(_styleInit)        
   
    def _styleShutdown(style, uri, data):
        # Cleanup all the document instances we were using.
        DbXslExtension.instance.cleanupList = []
            
    _styleShutdown = Callable(_styleShutdown)