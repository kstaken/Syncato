#!/usr/local/bin/python
#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.
#
# $Id: BaseDatabase.py,v 1.9 2003/12/15 14:57:48 kstaken Exp $

import sys, time, os
import xmlrpclib

from string import replace

import XSLExtensions

from XMLFragment import *
from Exceptions import *

from base64 import encodestring
from threading import *

import logging
import libxml2, libxslt
          
# Name of the document in the database that contains the current modification
# status of the database.
DB_STATUS = "db-status" 

# The starting point for ID allocations
INITIAL_ID = 500

# The name of the file that holds configurations for data types
DATATYPE_CONFIG = "config.xml"

class BaseDatabase:
    theInstance = None
    
    def __init__(self, config):        
        self.config = config
        
        registerNamespaces(config.xpathEval("/blog/namespace"))
        
        self.mutex = RLock()
        
        logging.basicConfig()
        # Configure logging for this class
        self.log = logging.getLogger("Database")
        self.log.setLevel(logging.DEBUG)
        
        if (not os.path.exists(self.configValue("/blog/cache-location"))):
            os.mkdir(self.configValue("/blog/cache-location"))
            
        # Register our libxsl extension functions
        XSLExtensions.registerExtensions()
        
        self.dataConfig = self._loadDatabaseConfig()
                                
    def configValue(self, xpath, default=""):
        results = self.config.xpathEval(xpath)
        if (len(results) > 0):
            return results[0].content
        else:
            return default
            
    def xpathQueryRecord(self, recordID, xpath):
        """
        Runs an XPath query against a particular document. This is done using 
        the libxml2 XPath engine due to limitations in the current DB XML Python
        API.
        """
        return self.queryDocument(self.getRecord(None, recordID), xpath)
        
    def queryDocument(self, content, xpath):
        doc = XMLFragment(content)
        
        result = XMLFragment()
        results = doc.xpathEval(xpath)          

        if (len(results) > 0):
            root = result.getFragment().newChild(None, "results", None)
            for item in results:
                item.unlinkNode()
                item.reconciliateNs(doc.getDocument())
                content = item.serialize()     
                
                root.addChild(item)
                
            return result.serialize()
        else:
            return '<?xml version="1.0"?><results/>'
            
    def _prepareDocument(self, record):
        doc = record
        if (isinstance(record, str)):
            doc = XMLFragment(record)                            
        
        root = doc.getRootElement()
        
        # Add the date if it's not already there.
        if (0 == len(doc.xpathEval("//pubDate"))):                            
            date = time.time()
            # ISO8601 Date
            # TODO this shouldn't really use localtime as the ISO8601 date should be GMT. Just not sure how to 
            # convert the time using XSL-T otherwise.
            pubDate = root.newChild(None, "pubDate", time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(date)) + "-07:00")
 
            pubDate.setProp("seconds", str(date))

        # Set the id for the post
        # TODO: maybe this would be better as meta-data or should at least
        # be in a namespace            
        # This call will also mark the database as modified
        # TODO: see if there's a better way.
        recordID = self.getNextID()
        root.setProp("id", str(recordID))

        return(doc, recordID)
        
    def runTransform(self, data, stylesheetName, arg, defaultStylesheet = ""):
        # Find the actual location for the stylesheet
        stylesheet = self.locateStylesheet(stylesheetName)
        if (stylesheet == None):
            # if the stylesheet wasn't found try for the default style
            if (defaultStylesheet != ""):
                stylesheet = self.locateStylesheet(defaultStylesheet)

            if (stylesheet == None):
                # TODO this should throw an exception
                self.log.error("Stylesheet implementation could not be found for %s" % stylesheetName)
                return ""
            
        resultXML = ""
        # Parse the stylesheet
        self.mutex.acquire()
        try:
            from time import clock
                
            # TODO: room for optimization, should also make sure it's OK for
            # libxslt to run with multiple threads.
            style = None
            try:
                starttime = clock()
        
                styledoc = libxml2.parseFile(stylesheet)
                style = libxslt.parseStylesheetDoc(styledoc)
                doc = XMLFragment(data)
                self.log.debug(str(clock() - starttime) + " seconds for xsl parse") 
            except:
                self.log.exception("Error parsing stylesheet %s" % stylesheet)
                raise
            
            starttime = clock()    
            result = XMLFragment(style.applyStylesheet(doc.getFragment(), {
                'arg': '"' + arg + '"',
                'site_id': '"' + self.configValue("/blog/id") + '"'
                }))
            
            if not(result.serialize() == '<?xml version="1.0"?>\n'):
                resultXML = style.saveResultToString(result.getFragment())
            self.log.debug(str(clock() - starttime) + " seconds for xsl execution")
        finally:
            if (style != None):
                style.freeStylesheet()
            self.mutex.release()
            #styledoc.freeDoc()
            #result.freeDoc()
            
        
        return resultXML        
        
    def locateStylesheet(self, stylesheet):
        return self.locateFile(stylesheet, ".xsl")
        
    def locateFile(self, filename, extension):
        """
        Searches the system and user stylesheet directories to locate the 
        file. The user directory is checked first and any stylesheets
        placed there will override those in the system directory.
        """
        # If it's an absolute path we just return it
        if (filename.startswith("/")):
            return filename
        # Otherwise we check the user stylesheet directory then system
        else:
            filename = replace(filename, extension, "")
            
            directories = [self.configValue("/blog/user-style-location"), self.configValue("/blog/system-style-location")]
            for directory in directories:
                files = os.listdir(directory)
                for file in files:
                    if (file.endswith(extension)):
                        # Strip the extension just to be sure
                        file = replace(file, extension, "")
                        if (file == filename):
                            return directory + "/" + file + extension 
                            
                    # Check sub directories
                    elif (os.path.isdir(directory + "/" + file) and filename.startswith(file)):
                        subdirFiles = os.listdir(directory + "/" + file)
                        for subdirFile in subdirFiles:
                            # Strip the extension just to be sure
                            subdirFile = replace(subdirFile, extension, "")
                            
                            if (file + "/" + subdirFile == filename):
                                return directory + "/" + file + "/" + subdirFile + extension 


    def _loadDatabaseConfig(self):
        """
        Loads the configurations for all datatypes.
        
        Configurations are stored in the file config.xml in each datatypes 
        directory.
        """
        datatypes = "<datatypes>"
        directories = [self.configValue("/blog/user-style-location"), self.configValue("/blog/system-style-location")]
        for directory in directories:
            files = os.listdir(directory)
            for file in files:        
                # Datqtypes are stored in sub directories
                if (os.path.isdir(directory + "/" + file)):
                    subdirFiles = os.listdir(directory + "/" + file)
                    for subdirFile in subdirFiles:
                        if (subdirFile == DATATYPE_CONFIG):
                            data = open(directory + "/" + file + "/" + subdirFile).read()
                            datatypes += data
                            
        datatypes += "</datatypes>"
        
        return XMLFragment(datatypes)
        
    def _applyTriggers(self, txn, action, record):
        if (isinstance(record, str)):
            record = XMLFragment(record)
    
        rootName = record.getRootElement().name
        
        self.log.debug("_applyTriggers: handling %s for type %s" % (action, rootName))
        
        # See if there are any reference triggers for this type of item and this
        # action
        query = "/datatypes/datatype/relation[@from-type = '%s']/trigger[on = '%s']"
        query = query % (rootName, action)
        self.log.debug("_applyTriggers: looking for triggers with query %s" % query)
        
        self._runTriggers(txn, query, record)        
        
        # Handle any references for actions that should occur for the same 
        # datatype
        query = "/datatypes/datatype[@root='%s']/trigger[on='%s']"
        query = query % (rootName, action)
        self.log.debug("_applyTriggers: looking for triggers with query %s" % query)
        
        self._runTriggers(txn, query, record)
        
    def _runTriggers(self, txn, query, record):
        """
        Runs the query against the data configuration and runs any triggers
        that if finds.
        """
        triggers = self.dataConfig.get(query)        
        # The result is a list of triggers to execute
        for trigger in triggers:
            self.log.debug("Processing trigger %s" % trigger.getValue("action/@name")) 
            self._executeTrigger(txn, trigger, record)
        
    def _executeTrigger(self, txn, trigger, record):
        # find out what trigger action this should perform
        actionName = trigger.getValue("action/@name")
        
        action = trigger.getSingle("action")        
        
        self.triggers = {}
        self.triggers["cascade"] = self._cascadeDeletes
        self.triggers["increment"] = self._increment
        self.triggers["decrement"] = self._decrement
        self.triggers["send-pings"] = self._pingWeblogs
                
        # Find the trigger method to call
        triggerMethod = self.triggers[actionName]
        if (triggerMethod):            
            triggerMethod(txn, record, action)
            self.log.debug("Calling trigger method %s" % (actionName))            
        else:
            self.log.warn("Unknown trigger method %s" % (actionName))
            
    def _increment(self, txn, record, params):
        self.log.debug("increment called")
        
        targetPath = params.getValue("param[@name='target-path']")
        keyPath = params.getValue("param[@name='key-path']")
        
        # We get the key data that we should look for in the related documents. 
        targetID = record.getValue(keyPath)
        try:
            self.log.debug("increment retrieving record " + targetID)        
            target = XMLFragment(self.getRecord(txn, targetID))
            self.log.debug("increment record retrieved")        
                        
            result = target.getSingle(targetPath)            
            # See whether we should update the count or add the element
            if (result != None):
                count = int(result.getContent())
                result.setContent(str(count + 1))
            else:
                nodeName = targetPath.split("/")[-1]
                target.getRootElement().newChild(None, nodeName, "1")
        
            self.log.debug("increment saving modified record")        
            self.updateRecord(txn, targetID, target.serialize())
            
        except NotFoundError:
            self.log.warn("increment called for non-existent target")
        
    def _decrement(self, txn, record, params):
        self.log.debug("decrement called")
        
        targetPath = params.getValue("param[@name='target-path']")
        keyPath = params.getValue("param[@name='key-path']")
        
        # We get the key data that we should look for in the related documents. 
        targetID = record.getValue(keyPath)
        try:
            target = XMLFragment(self.getRecord(txn, targetID))
            
            result = target.getSingle(targetPath)            
            if (result != None):
                count = int(result.getContent()) - 1
                if (count < 0):
                    count = 0
                result.setContent(str(count))
                
                self.updateRecord(txn, targetID, target.serialize())

        except NotFoundError:
            self.log.warn("decrement called for non-existent target")
        
        
    def _cascadeDeletes(self, txn, record, params):
        targetRoot = params.getValue("param[@name='target-root']")
        fromKey = params.getValue("param[@name='from-key']")
        targetKey = params.getValue("param[@name='target-key']")
        
        # We get the key data that we should look for in the related documents. 
        relation = record.getValue("/%s/%s" % (record.getRootElement().name, fromKey))
        
        if (relation != ""):
            # Now build the query to select the ids for the target documents
            query = "/%s[%s=%s]/@id" % (targetRoot, targetKey, relation)
            related = XMLFragment(self.xpathQuery(txn, query))
            content = related.getRootElement().content.strip()
            if (content != ""):
                for id in content.split("\n"):
                    try:
                        self.deleteRecord(txn, id)
                    except NotFoundError:
                        self.log.warn("_cascadeDeletes: Deleting %s, but it's already gone" % id)
    
    def _pingWeblogs(self, txn, record, params):
        """
        Send change notification pings to sites that list weblog changes, we put
        this in a separate thread so that posting can be quick. There's little
        benefit in waiting for the results from this.
        """    
        if (self.configValue("/blog/ping-weblogs") == "yes"):
            thread = Thread(target=self._sendPings)
            thread.start()
                       
    def _sendPings(self):
        """
        Send change notification pings to sites that list weblog changes
        """        
        
        try:
            # get a list of sites to ping.
            sites = self.config.xpathEval("/blog/ping-target")
            
            for site in sites:
                self.log.info('pinging ' + site.content)
                # ping each site
                server = xmlrpclib.Server(site.content)        
                server.weblogUpdates.ping(self.configValue("/blog/title"), self.configValue("/blog/base-url"))  
        except:
            # this failing is a non-critical error
            pass
            
    def shutdown(self):
        # abstract
        pass
    
    def getRecord(self, txn, recordID):
        # abstract
        pass
    
    def addRecord(self, txn, record):
        # abstract
        pass
    
    def updateRecord(self, txn, recordID, record):
        # abstract
        pass
    
    def deleteRecord(self, txn, recordID):
        # abstract
        pass

    def beginTransaction(self):
        # abstract
        pass

    def commitTransaction(self, txnID):
        # abstract
        pass

    def abortTransaction(self, txnID):
        # abstract
        pass
        
    def _checkCache(self, pathInfo, stylesheet, arg, contentQuery):
        cachekey = self._cacheKey(pathInfo, stylesheet, arg, contentQuery)
                       
        result = ""        
        try:       
            cacheLocation = self.configValue("/blog/cache-location") + "/" + cachekey
            
            self.mutex.acquire()
                
            if (os.path.exists(cacheLocation)):
                stats = os.stat(cacheLocation)
                                
                if (stats.st_mtime > self.modifiedTime):
                    file = open(cacheLocation, "r")
                    result = file.read()
                    file.close()
                else:
                    os.remove(cacheLocation)                    
        finally:
            self.mutex.release()
            
        return result
        
    def _saveToCache(self, pathInfo, stylesheet, arg, contentQuery, result):
        """
        Adds an entry to the cache for the current document. Cache entries are
        specific to a particular stylesheet and pathInfo path.
        """   
        # see if the entry may have been added to the cache by another thread
        try:
            self.mutex.acquire()
            
            if (self._checkCache(pathInfo, stylesheet, arg, contentQuery) == ""):
                
                cachekey = self._cacheKey(pathInfo, stylesheet, arg, contentQuery)
                
                cacheLocation = self.configValue("/blog/cache-location") + "/" + cachekey
                file = open(cacheLocation, "w")
                file.write(result)
                file.close()
        finally:
            self.mutex.release()     
           
    def _cacheKey(self, pathInfo, stylesheet, arg, contentQuery):
        cachekey = pathInfo + "|" + stylesheet + "|" + arg + "|" + contentQuery
        cachekey = encodestring(cachekey)
        cachekey = cachekey.strip()
        
        # / is a legal character for base64, but is illegal for the file system
        # # will not appear in a base64 encoding but is OK to the file system
        cachekey = replace(cachekey, "/", "#")
        
        return cachekey
