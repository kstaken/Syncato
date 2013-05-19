#!/usr/local/bin/python
#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.
#  
# $Id: DBXMLDatabase.py,v 1.7 2004/02/18 08:10:40 kstaken Exp $

import sys, time, os
import xmlrpclib

from bsddb.db import *
from dbxml import *

from BaseDatabase import *

from threading import RLock

import libxml2, libxslt
           
class DBXML2Database (BaseDatabase):
    theInstance = None
    
    def __init__(self, config):             
        BaseDatabase.__init__(self, config)
        
        self.config = config
        
        # Setup the Berkeley DB XML environment and open the container        
        self.environment = DBEnv()
        self.environment.open(self.configValue("/blog/db-location"), DB_CREATE|DB_INIT_LOCK|DB_INIT_LOG|DB_INIT_MPOOL|DB_INIT_TXN|DB_THREAD|DB_RECOVER, 0)
        
        self.log.info("Opened environment")        
        
        self.manager = XmlManager(self.environment, 0)        
        txn = self.manager.createTransaction()
        self.db = self.manager.openContainer(txn, "blog.dbxml", DB_CREATE|DBXML_TRANSACTIONAL)

        self._addIndexes(txn)
        
        txn.commit(0)
        
        self.log.info("Opened blog.dbxml")
        
        self._initDBStatus()
                    
    def __del__(self): 
        self.shutdown()
        
    def shutdown(self):        
        #if (self.db.isOpen()):
        #self.config.freeDoc()
        self.log.info("Closing databases")
        #del self.db
        #del self.manager
        #del self.environment
        #self.environment.close(0)
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
                      
            document = self.manager.createDocument()
            document.setContent(doc.serialize())     
            document.setName(str(recordID))                  
        except libxml2.parserError, e:
            raise ParseError(e)

        # Save the entry to the database
        autocommit = 0
        try:
            if (txn == None):
                self.log.debug("addRecord creating new transaction")
                txn = self.manager.createTransaction()
                autocommit = 1

            uc = self.manager.createUpdateContext()
            self.db.putDocument(txn, document, uc)
        
            self._applyTriggers(txn, "insert", document.getContentAsString())
    
            if (autocommit == 1):
                self.log.debug("addRecord autocommiting transaction")
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
                txn = self.manager.createTransaction()
                autocommit = 1            

            document = self.getRecordDocument(txn, recordID)

            # Make sure the ID is set on the new content
            doc = XMLFragment(record)    
            root = doc.getRootElement()            
            root.setProp("id", str(recordID))

            # Update the document
            document.setContent(doc.serialize())
            
            uc = self.manager.createUpdateContext()
            self.db.updateDocument(txn, document, uc)
            
            self._applyTriggers(txn, "update", document.getContentAsString())
            
            if (autocommit == 1):
                self.log.debug("updateRecord autocommiting transaction")
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
                txn = self.manager.createTransaction()
                autocommit = 1
            
            document = self.getRecordDocument(txn, recordID).getContent()
            uc = self.manager.createUpdateContext()
            self.db.deleteDocument(txn, str(recordID), uc)
            
            self._applyTriggers(txn, "delete", document)
    
            if (autocommit == 1):                
                self.log.debug("deleteRecord autocommiting transaction")
                txn.commit(0)
                        
                # Mark the database as modified
                self._updateDBStatus()                
        except Exception, e:
            if (autocommit == 1):
                #self.log.exception("deleteRecord Aborting transaction")
                txn.abort()
            raise
        
    def getRecordDocument(self, txn, recordID):                    
        autocommit = 0
        try:
            if (txn == None):            
                result = self.db.getDocument(str(recordID))
            else:
                result = self.db.getDocument(txn, str(recordID))
                
            return result
        except:
            raise NotFoundError
        
    def getRecord(self, txn, recordID):
        try:            
            return self.getRecordDocument(txn, recordID).getContent()            
        except:
            raise NotFoundError
    
    def _prepareContext(self):
        context = self.manager.createQueryContext()
        #context.setReturnType(XmlQueryContext.CandidateDocuments)
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
        if (txn == None):
            results = self.manager.query("collection('blog.dbxml')" + xpath, context)
        else:
            results = self.manager.query(txn, "collection('blog.dbxml')" + xpath, context)
        
        self.log.debug("xpathQuery: executing " + xpath + " found " + str(results.size()) + " results ")
            
        finalResult =  u'<?xml version="1.0"?><results/>'
        #if (results.size() > 0):
        xmlResult = [u'<?xml version="1.0"?><results>']
        for item in results:            
            content = item.asDocument().getContent()                
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

        xmlResult.append(u"</results>")
        
        self.log.debug(str(clock() - starttime) + " seconds for query " + xpath)

        finalResult = "\n".join(xmlResult)
        
       # self._applyTriggers(txn, "query", finalResult)
        
        #TODO much needed error handling
        return finalResult

    def _addIndexes(self, txn):
        uc = self.manager.createUpdateContext()
        
        self.db.addIndex(txn, "", "seconds", "node-attribute-equality-decimal", uc)
        self.db.addIndex(txn, "", "id", "node-attribute-equality-decimal", uc)
        
        self.db.addIndex(txn, "", "category", "node-element-equality-string", uc) 
        self.db.addIndex(txn, "", "category-def", "node-element-presence-none", uc)  
        self.db.addIndex(txn, "", "item", "node-element-presence-none", uc)  
        self.db.addIndex(txn, "", "comment", "node-element-presence-none", uc)
        self.db.addIndex(txn, "", "trackback", "node-element-presence-none", uc)  
        
        self.db.addIndex(txn, "", "blacklist", "node-element-presence-none", uc) 
        self.db.addIndex(txn, "", "url", "node-element-equality-string", uc)
        #self.db.addIndex(txn, "", "blacklist/url", "edge-element-equality-string", uc)
        
        self.db.addIndex(txn, "", "title", "node-element-equality-string", uc)        
        #self.db.addIndex(txn, "", "item/title", "edge-element-equality-string", uc)
        
        self.db.addIndex(txn, "", "postID", "node-attribute-equality-decimal", uc)
        #self.db.addIndex(txn, "", "trackback/postID", "edge-attribute-equality-number", uc)
            
    def _initDBStatus(self):
        """
        db-status is used to track modifications to the database so that cache 
        files can be re-generated. It also contains the next id that will be 
        used when creating new entries.
        """
        # See if there's already a database status document in the database.        
        try:
            self.dbStatus = self.getRecordDocument(None, DB_STATUS)

            doc = libxml2.parseDoc(self.dbStatus.getContent())

            self.modifiedTime = float(doc.xpathEval("/status/db-status")[0].content)            
            self.nextID = int(doc.xpathEval("/status/next-id")[0].content)

            doc.freeDoc()        
        except:
            # If not we need to add it to the database.
            # The status entry always gets id 499
            metadata = "<status id='"  + str(INITIAL_ID - 1) + "'><db-status>0</db-status><next-id>" + str(INITIAL_ID) + "</next-id></status>"
            document = self.manager.createDocument()
            document.setContent(metadata)
            document.setName(DB_STATUS)
            
            txn = self.manager.createTransaction()
            try:
                uc = self.manager.createUpdateContext()
                self.db.putDocument(DB_STATUS, metadata, uc)
                txn.commit(0)
            except:
                print "FAILED saving the DB_STATUS record"
                txn.abort()
                
            self.dbStatus = document
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
            
            document = self.dbStatus
            document.setContent(newStatus)
            
            txn = self.manager.createTransaction()
            try:
                uc = self.manager.createUpdateContext()
                self.db.updateDocument(txn, document, uc)
                txn.commit(0)   
            except:
                txn.abort()
        finally:
            self.mutex.release()
            
