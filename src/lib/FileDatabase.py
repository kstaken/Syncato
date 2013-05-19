#!/usr/local/bin/python
#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.
#  
# $Id: FileDatabase.py,v 1.3 2003/12/15 14:57:48 kstaken Exp $

import sys, time, os
import xmlrpclib

from string import replace

from BaseDatabase import *
from XMLFragment import XMLFragment

from threading import RLock

import libxml2, libxslt
           
class FileDatabase (BaseDatabase):
    theInstance = None
    
    def __init__(self, config):  
        BaseDatabase.__init__(self, config)

        self.config = config
        
        # Make sure the database directory exists.
        if (not os.path.exists(self.configValue("/blog/db-location"))):
            os.mkdir(self.configValue("/blog/db-location"))
        
        self.dbPath = self.configValue("/blog/db-location") + "/"
        
        self._initDBStatus()
        self.open = 1
        
    def __del__(self): 
        self.shutdown()
        
    def shutdown(self):
        if (self.open == 1):
            self.log.info("Closing databases")
            self.config.freeDoc()
            self.open = 0
            
    def getNextID(self):
        """
        Get the ID to use for the next record that's created.
        """
        
        # Only one thread allowed at a time.        
        self.mutex.acquire()
        try:
            result = self.nextID
            self.nextID += 1
            
            self._updateDBStatus()
            return result
        finally:
            self.mutex.release()
            
    def addRecord(self, txn, record):
        if (record == None):
            raise ParseError("No content specified")

        recordID = 0
        try:
            (doc, recordID) = self._prepareDocument(record)
            
            file = open(self.dbPath + str(recordID) + ".xml", "w")
            
            file.write(doc.serialize())
            file.close()
            
            self._applyTriggers(txn, "insert", doc)
                
            return recordID  
        except libxml2.parserError, e:
            raise ParseError(e)
              
            
    def updateRecord(self, txn, recordID, record):      
        if (record == None):
            raise ParseError
            
        try:
            fileName = self.dbPath + str(recordID) + ".xml"
            if (not os.path.exists(fileName)):
                raise NotFoundError
                
            # Make sure the ID is set on the new content
            doc = XMLFragment(record)    
            root = doc.getRootElement()            
            root.setProp("id", str(recordID))
        
            # Update the document
            file = open(fileName, "w")
            
            file.write(doc.serialize())
            file.close()
            
            self._applyTriggers(txn, "update", doc)          
        except libxml2.parserError, e:
            raise ParseError(e)
        except Exception, e:
            raise e
            
        # Mark the database as modified
        self._updateDBStatus()            
            
    def deleteRecord(self, txn, recordID):
        if (recordID == None):
            raise NotFoundError
            
        try:
            document = self.getRecord(txn, recordID)
            os.remove(self.dbPath + str(recordID) + ".xml")
            
            self._applyTriggers(txn, "delete", XMLFragment(document))
    
            # Mark the database as modified
            self._updateDBStatus()                
        except:
            #self.log.exception("Failed deleting document %s", recordID)
            raise NotFoundError
        
    def getRecord(self, txn, recordID):
        fileName = self.dbPath + str(recordID) + ".xml"
        
        if (os.path.exists(fileName)):
            file = open(fileName)
            result = file.read()
            file.close()
            return result
        else:
            raise NotFoundError
              
    def xpathQuery(self, txn, xpath):        
        xmlResult = [u'<?xml version="1.0"?><results>']
        
        files = os.listdir(self.dbPath)
        for file in files:
            doc = XMLFragment(open(self.dbPath + "/" + file).read())
            results = doc.xpathEval(xpath)
            for result in results:
                result.unlinkNode()
                result.reconciliateNs(doc.getDocument())
                content = result.serialize()
                if (content.startswith("<")):
                    xmlResult.append(content)
                else:
                    xmlResult.append(result.content)
                      
        xmlResult.append(u"</results>")
        
        #self._applyTriggers(txn, "query", XMLFragment("\n".join(xmlResult)))
        
        return u"\n".join(xmlResult)
                        
    def _initDBStatus(self):
        """
        db-status is used to track modifications to the database so that cache 
        files can be re-generated. It also contains the next id that will be 
        used when creating new entries.
        """
        # See if there's already a database status document in the database.        
        try:
            dbStatus = self.getRecord(None, DB_STATUS)
            doc = libxml2.parseDoc(dbStatus)
            self.dbStatus = doc
            
            self.modifiedTime = float(doc.xpathEval("/status/db-status")[0].content)            
            self.nextID = int(doc.xpathEval("/status/next-id")[0].content)
           
        except NotFoundError:
             # If not we need to add it to the database.
            metadata = "<status><db-status>0</db-status><next-id>" + str(INITIAL_ID) + "</next-id></status>"
            
            file = open(self.dbPath + str(DB_STATUS) + ".xml", "w")
            file.write(metadata)
            file.close()
                
            self.dbStatus = libxml2.parseDoc(metadata)
            self.modifiedTime = 0
            self.nextID = INITIAL_ID

            
    def _updateDBStatus(self):
        """
        Updates the state of the database with the last modification time
        """        
        self.mutex.acquire()
        try:
            self.modifiedTime = time.time()
            
            newStatus = "<status><db-status>" + str(self.modifiedTime) + "</db-status>"
            newStatus += "<next-id>" + str(self.nextID) + "</next-id></status>"
            
            file = open(self.dbPath + str(DB_STATUS) + ".xml", "w")
            file.write(newStatus)
            file.close()
        finally:
            self.mutex.release()
            
