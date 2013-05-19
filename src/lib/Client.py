#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.

import WeblogUtil
import re
import libxml2

class Client:
    
    def __init__(self, host, baseURL, username, password):
        self.host = host
        self.baseURL = baseURL
        self.username = username
        self.password = password
        
    def xpathQuery(self, url, xpath):
        pass
        
    def getRecord(self, recordID):
        """
        Reads an XML entry from the database
        """
        recordID = self.cleanRecordID(recordID)
        
        result = self._runRequest("GET", recordID)
        
        if (result.status == 200):
            data = result.read().strip()
                        
            return data
        else:
            return None
            
    def addRecord(self, entry):
        """
        Adds an XML entry to the database.
        """
        result = self._runRequest("POST", self.baseURL, entry)
        
        if (result.status == 201):
            location = result.getheader("Location")
            
            return location
        else:
            return ""

    def updateRecord(self, recordID, body):        
        """
        Updates an XML entry in the database
        """
        recordID = self.cleanRecordID(recordID)
           
        return self._runRequest("PUT", recordID, body)
                        
    def deleteRecord(self, recordID):
        """
        Deletes an XML entry from the database
        """
        recordID = self.cleanRecordID(recordID)
        
        return self._runRequest("DELETE", recordID)
          
    def cleanRecordID(self, recordID):
        """
        Strips the host and protocol from the recordID
        """
        stripHTTP = re.compile(r"http://.+?/", re.IGNORECASE)
        if (recordID.startswith("http://")):
            recordID = "/" + stripHTTP.sub("", recordID)
          
        return recordID
        
    def _runRequest(self, method, url, body = ""): 
        return WeblogUtil.runRequest(self.host, self.username, 
            self.password, method, url, body)