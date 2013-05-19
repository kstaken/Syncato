#!/usr/local/bin/python
#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.
#  
# $Id: DBXMLDatabase.py,v 1.7 2004/02/18 08:10:40 kstaken Exp $

import sys, time, os
import xmlrpclib

from bsddb3.db import *
from dbxml import *

from BaseDatabase import *

from threading import RLock

import libxml2, libxslt
           
class DBXMLDatabase (BaseDatabase):
    theInstance = None
    
    def __init__(self, config):             
        BaseDatabase.__init__(self, config)
        
        self.config = config
        
        
        self.environment = DBEnv()
        #self.environment.open(self.configValue("/blog/db-location"), DB_CREATE | DB_INIT_CDB  | DB_INIT_MPOOL | DB_THREAD, 0)
        self.environment.open(self.configValue("/blog/db-location"), DB_CREATE|DB_INIT_LOCK|DB_INIT_LOG|DB_INIT_MPOOL|DB_INIT_TXN|DB_THREAD|DB_RECOVER, 0)
        
        self.log.info("Opened environment")        
        txn = self.environment.txn_begin()
        self.log.info("starting tx")        
        
        # Open the main database
        self.db = XmlContainer(self.environment, "blog.dbxml")
        
        self.db.open(txn, DB_CREATE)
        self.log.info("Opened container")        
        
        #self.db.setLogCategory(CATEGORY_ALL, True)
        #self.db.setLogLevel(LEVEL_DEBUG, True)
        
        self.log.info("Opened blog.dbxml")
        
        #self._addIndexes(txn)
        
        txn.commit(0)
            
        self._initDBStatus()
                    
    def __del__(self): 
        self.shutdown()
        
    def shutdown(self):        
        if (self.db.isOpen()):
            self.config.freeDoc()
            self.log.info("Closing databases")
            self.db.close()
            self.environment.close(0)
            #self.open = 0
            
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
                      
            document = XmlDocument()
            document.setContent(doc.serialize())                       
        except libxml2.parserError, e:
            raise ParseError(e)
              
        # Save the entry to the database
        autocommit = 0
        try:
            if (txn == None):
                self.log.debug("addRecord creating new transaction")
                txn = self.environment.txn_begin()
                autocommit = 1
            
            self.db.putDocument(txn, document)
        
            self._applyTriggers(txn, "insert", document.getContentAsString())
    
            if (autocommit == 1):
                txn.commit(0)
                
            return recordID
        except Exception, e:            
            if (autocommit == 1):
                txn.abort()
            self.log.exception("addRecord: failure adding new record")
            
    def updateRecord(self, txn, recordID, record):
        if (record == None):
            raise ParseError

        autocommit = 0
        try:
            if (txn == None):
                self.log.debug("updateRecord: Creating new transaction")
                txn = self.environment.txn_begin()
                autocommit = 1            

            document = self.getRecordDocument(txn, recordID)
            
            # Make sure the ID is set on the new content
            doc = XMLFragment(record)    
            root = doc.getRootElement()            
            root.setProp("id", str(recordID))
        
            # Update the document
            document.setContent(doc.serialize())
            self.db.updateDocument(txn, document)
            
            self._applyTriggers(txn, "update", document.getContentAsString())
            
            if (autocommit == 1):
                txn.commit(0)
                
                # Mark the database as modified
                self._updateDBStatus()            

        except libxml2.parserError, e:
            if (autocommit == 1):
                txn.abort()
            raise ParseError(e)
        except Exception, e:
            if (autocommit == 1):
                txn.abort()
            raise e
            
    def deleteRecord(self, txn, recordID):
        if (recordID == None):
            raise NotFoundError
            
        autocommit = 0
        try:
            if (txn == None):
                self.log.debug("deleteRecord creating new transaction")
                txn = self.environment.txn_begin()
                autocommit = 1
            
            document = self.getRecordDocument(txn, recordID)
            self.db.deleteDocument(txn, document)
            
            self._applyTriggers(txn, "delete", document.getContentAsString())
    
            if (autocommit == 1):                
                self.log.debug("deleteRecord autocommiting transaction")
                txn.commit(0)
                        
                # Mark the database as modified
                self._updateDBStatus()                
        except Exception, e:
            if (autocommit == 1):
                #self.log.exception("Aborting transaction")
                txn.abort()
            raise
        
    def getRecordDocument(self, txn, recordID):            
        query = "/node()[@id=%s]" % recordID
        
        self.log.debug("getrecordDocument query %s" % query)
        results = self.db.queryWithXPath(txn, query, None)
        if (results.size() > 0):
            return results.next().asDocument()
        else:
            raise NotFoundError
        
    def getRecord(self, txn, recordID):
        try:            
            return self.getRecordDocument(txn, recordID).getContentAsString()            
        except:
            raise NotFoundError
    
    def _prepareContext(self):
        context = XmlQueryContext()
        context.setReturnType(XmlQueryContext.CandidateDocuments)
        #context.setReturnType(XmlQueryContext.ResultValues)
        
        for namespace in self.config.xpathEval("/blog/namespace"):
            prefix = namespace.prop("prefix")
            url = namespace.content
            context.setNamespace(prefix, url)
            
        return context
        
    def xpathQuery(self, txn, xpath):
        context = self._prepareContext()
        
        from time import clock
        starttime = clock()
        # Run xpath against the database
        results = self.db.queryWithXPath(txn, xpath, context)
        
        finalResult =  u'<?xml version="1.0"?><results/>'
        if (results.size() > 0):
            xmlResult = [u'<?xml version="1.0"?><results>']
            for item in results:            
                content = item.asString()                
                doc = XMLFragment(content)
                results = doc.xpathEval(xpath)
                
                for result in results:    
                    result.unlinkNode()
                    result.reconciliateNs(doc.getDocument())
                    content = result.serialize()     
                    if (content.startswith("<")):
                        xmlResult.append(content)
                    else:
                        xmlResult.append(result.content)
                
                    #xmlResult.append(replace(content, u'<?xml version="1.0"?>', u''))                    
                                    
            xmlResult.append(u"</results>")
               
            #doc = libxml2.parseDoc("\n".join(xmlResult))
            #results = doc.xpathEval("/results" + xpath)
            #libDoc = libxml2.newDoc("1.0")
            #root = libDoc.newChild(None, "results", None)
            
            #for result in results:
            #    result.unlinkNode()
            #    root.addChild(result)
          
            #finalResult = libDoc.serialize()
            #libDoc.freeDoc()
            
            self.log.debug(str(clock() - starttime) + " seconds for query " + xpath)
            #return result
            #print "\n".join(xmlResult)
            finalResult = "\n".join(xmlResult)
        
       # self._applyTriggers(txn, "query", finalResult)
        
        #TODO much needed error handling
        return finalResult

    def _addIndexes(self, txn):
        self.db.addIndex(txn, "", "seconds", "node-attribute-equality-number")
        self.db.addIndex(txn, "", "id", "node-attribute-equality-number")
        
        self.db.addIndex(txn, "", "category", "node-element-equality-string") 
        self.db.addIndex(txn, "", "category-def", "node-element-presence-none")  
        self.db.addIndex(txn, "", "item", "node-element-presence-none")  
        self.db.addIndex(txn, "", "comment", "node-element-presence-none")
        self.db.addIndex(txn, "", "trackback", "node-element-presence-none")  
        
        self.db.addIndex(txn, "", "blacklist", "node-element-presence-none") 
        self.db.addIndex(txn, "", "url", "node-element-equality-string")
        #self.db.addIndex(txn, "", "blacklist/url", "edge-element-equality-string")
        
        self.db.addIndex(txn, "", "title", "node-element-equality-string")        
        #self.db.addIndex(txn, "", "item/title", "edge-element-equality-string")
        
        self.db.addIndex(txn, "", "postID", "node-attribute-equality-number")
        #self.db.addIndex(txn, "", "trackback/postID", "edge-attribute-equality-number")
            
    def _initDBStatus(self):
        """
        db-status is used to track modifications to the database so that cache 
        files can be re-generated. It also contains the next id that will be 
        used when creating new entries.
        """
        # See if there's already a database status document in the database.        
        results = self.db.queryWithXPath(None, "/status[" + DB_STATUS + "]", None)
        if (results.size() == 0):
            # If not we need to add it to the database.
            # The status entry always gets id 499
            metadata = "<status id='"  + str(INITIAL_ID - 1) + "'><db-status>0</db-status><next-id>" + str(INITIAL_ID) + "</next-id></status>"
            document = XmlDocument()
            document.setContent(metadata)
            document.setName(DB_STATUS)
            
            txn = self.environment.txn_begin()
            try:
                self.db.putDocument(txn, document)
                txn.commit(0)
            except:
                txn.abort()
                
            self.dbStatus = document
            self.modifiedTime = 0
            self.nextID = INITIAL_ID
        else:
            document = results.next().asDocument()
            self.dbStatus = document
            
            doc = libxml2.parseDoc(document.getContent())
            
            self.modifiedTime = float(doc.xpathEval("/status/db-status")[0].content)            
            self.nextID = int(doc.xpathEval("/status/next-id")[0].content)
            doc.freeDoc()        
            
    def _updateDBStatus(self):
        """
        Updates the state of the database with the last modification time
        """        
        self.mutex.acquire()
        try:
            self.modifiedTime = time.time()
            
            newStatus = "<status><db-status>" + str(self.modifiedTime) + "</db-status>"
            newStatus += "<next-id>" + str(self.nextID) + "</next-id></status>"
            
            document = self.dbStatus
            document.setContent(newStatus)
            
            txn = self.environment.txn_begin()        
            try:
                self.db.updateDocument(txn, document, None)
                txn.commit(0)   
            except:
                txn.abort()
        finally:
            self.mutex.release()
            
