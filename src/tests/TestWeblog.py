#!/usr/bin/env python
#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.

import libxml2

import httplib, unittest, os

from base64 import encodestring

testEntry = """<item>
    <title>Test Post 1</title>
    <description>Just a simple post to get started.</description>
    <category>XML</category>
    <category>Java</category>
</item>
"""

testEntry2 = """<item>
    <title>Test Post 2</title>
    <description>Just a simple post to get started. With modifications</description>
    <category>XML</category>
    <category>Python</category>
    <category>Java</category>
</item>
"""

REQUEST_URL = "/blog/"

USERNAME = "kstaken"
PASSWORD = "test"

class TestWeblog(unittest.TestCase):
    def setUp(self):
        self.conn = httplib.HTTPConnection("localhost:8080")
            
    def testAddPost(self):
        
        result = self.runRequest("POST", REQUEST_URL, testEntry)
        self.assertEqual(result.status, 201)
        self.assertEqual(result.reason, "Created")

        location = result.getheader("Location")
        self.assert_(location.startswith("http://"))
        # Read the content to clear the request
        result.read()

        result = self.runRequest("DELETE", location)	
       
    def testDeletePost(self):
        # Create a new entry
        result = self.runRequest("POST", REQUEST_URL, testEntry)
        location = result.getheader("Location")
        
        # Read the content to clear the request
        result.read()

        # Remove the entry
        result = self.runRequest("DELETE", location)	
        self.assertEqual(result.status, 200)
        self.assertEqual(result.reason, "OK")
        
        # Read the content to clear the request
        result.read()

        # Make sure it's gone, we should get a not found error
        result = self.runRequest("GET", location)
        self.assertEqual(result.status, 404)
        
        # Read the content to clear the request
        result.read()
        
        # Try to remove it again to remove a non-existent entry.
        # We should get a not found error
        result = self.runRequest("DELETE", location)	
        self.assertEqual(result.status, 404)
        
    def testGetPost(self):
        # Create a new entry
        result = self.runRequest("POST", REQUEST_URL, testEntry)
        location = result.getheader("Location")

        # Read the content to clear the request
        result.read()

        # Test retrieving that entry
        result = self.runRequest("GET", location)
        self.assertEqual(result.status, 200)
        self.assertEqual(result.reason, "OK")
        
        data = result.read().strip()
        doc = libxml2.parseDoc(data)
        title = doc.xpathEval("/item/title")[0].content
        self.assertEqual("Test Post 1", title)
        
        # Remove the entry
        result = self.runRequest("DELETE", location)	
        
        # Read the content to clear the request
        result.read()

        # Test retrieving it again for a non-existent entry
        result = self.runRequest("GET", location)
        self.assertEqual(result.status, 404)
        
    def testEditPost(self):
        # Create a new entry
        result = self.runRequest("POST", REQUEST_URL, testEntry)
        location = result.getheader("Location")

        # Read the content to clear the request
        result.read()

        # Update the content of that entry
        result = self.runRequest("PUT", location, testEntry2)
        self.assertEqual(result.status, 205)
        self.assertEqual(result.reason, "Reset Content")
        result.read()
        
        # Make sure the content is updated        
        result = self.runRequest("GET", location)
        self.assertEqual(result.status, 200)
        
        data = result.read().strip()
        doc = libxml2.parseDoc(data)
        title = doc.xpathEval("/item/title")[0].content
        self.assertEqual("Test Post 2", title)

        # Remove the entry
        result = self.runRequest("DELETE", location)

        # Read the content to clear the request
        result.read()
        
        # Try updating the entry again to test updating a non-existent entry
        result = self.runRequest("PUT", location, testEntry2)
        self.assertEqual(result.status, 404)
        
    def testGetPathDataForPost(self):
        # Create a new entry
        result = self.runRequest("POST", REQUEST_URL, testEntry)
        location = result.getheader("Location")

        # Read the content to clear the request
        result.read()

        # Test a query for a single XML result
        result = self.runRequest("GET", location + "/item/title")
        self.assertEqual(result.status, 200)
        self.assertEqual(result.reason, "OK")
        
        data = result.read().strip()
        doc = libxml2.parseDoc(data)
        title = doc.xpathEval("/results/title")[0].content
        self.assertEqual("Test Post 1", title)
 
        # Test a query for a single text result
        result = self.runRequest("GET", location + "/item/title/text()")
        self.assertEqual(result.status, 200)
        self.assertEqual(result.reason, "OK")
        
        data = result.read().strip()
        self.assertEqual("<?xml version=\"1.0\"?>\n<results>Test Post 1</results>", data)
       
        # Test a query for multiple XML results
        result = self.runRequest("GET", location + "/item/category")
        self.assertEqual(result.status, 200)
        self.assertEqual(result.reason, "OK")

        # We should get two categories in the results
        data = result.read().strip()
        doc = libxml2.parseDoc(data)
        categories = doc.xpathEval("/results/category")
        self.assertEqual(len(categories), 2)

        # Test a query for multiple text results
        result = self.runRequest("GET", location + "/item/category/text()")
        self.assertEqual(result.status, 200)
        self.assertEqual(result.reason, "OK")

        # We should get two categories, one per line in the results
        #categories = result.read().strip().split("\n")
        #self.assertEqual(len(categories), 2)
        #self.assert_(categories[0] == "XML" or categories[1] == "XML")
        # Read the content to clear the request
        result.read()
        
        # Remove the entry 
        result = self.runRequest("DELETE", location)

        # Read the content to clear the request
        result.read()
        
        # Test a query against a non-existent resource
        result = self.runRequest("GET", location + "/item/title")
        self.assertEqual(result.status, 404)

    def testGetRoot(self):
        result = self.runRequest("GET", REQUEST_URL)	
        self.assertEqual(result.status, 200)
        self.assertEqual(result.reason, "OK")
        self.assertEqual(result.getheader("Content-type"), "text/html")
        
    def testQueryRoot(self):
        # Create a new entry
        result = self.runRequest("POST", REQUEST_URL, testEntry)
        location = result.getheader("Location")

        # Read the content to clear the request
        result.read()
        
        # Run a query that selects XML nodes
        result = self.runRequest("GET", REQUEST_URL + "/item")	
        self.assertEqual(result.status, 200)
        self.assertEqual(result.reason, "OK")
        self.assertEqual(result.getheader("Content-type"), "text/xml")
        
        # Read the content to clear the request
        result.read()
        
        # Remove the entry 
        result = self.runRequest("DELETE", location)
        
    def runRequest(self, method, url, body = None):
        headers = {"Content-type": "text/xml"}
        self.conn.request(method, url, body, headers)
        
        result = self.conn.getresponse()
        
        # If we get a 403 response we need to authenticate
        if (result.status == 401):
            token = "Basic " + encodestring(USERNAME + ":" + PASSWORD).strip()
            headers = {"Content-type": "text/xml", "Authorization": token}
            self.conn.close()
            
            self.conn.request(method, url, body, headers)
        
            result = self.conn.getresponse()
            
        return result

if __name__ == "__main__":
    unittest.main()