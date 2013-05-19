#!/usr/bin/env python 
#
# Unit tests for the Databases

import sys
sys.path.append('../lib')

from Database import Database

import BaseDatabase

from XMLFragment import XMLFragment

import libxml2
import unittest, os
        
testEntry = """<item>
    <title>Test Post 1</title>
    <description>Just a simple post to get started.</description>
    <category>XML</category>
    <category>Java</category>
</item>
"""

testEntryNs = """<syncato:item xmlns:syncato="http://www.syncato.org/NS/syncato">
    <syncato:title>Test Post 1</syncato:title>
    <description>Just a simple post to get started.</description>
    <category>XML</category>
    <category>Java</category>
</syncato:item>
"""
         

class TestDatabase(unittest.TestCase):
        
    def __del__(self):
        self.db.shutdown()
            
    def testAddRecord(self):
        # Add an entry
        id = self.db.addRecord(None, testEntry)    
        self.assert_(id > 0)
        
        # Retrieve the entry we just added
        record = self.db.getRecord(None, id)
        
        # Compare it to the original document
        doc = libxml2.parseDoc(record)
        testDoc = libxml2.parseDoc(testEntry)
        
        title = doc.xpathEval("/item/title")[0].content        
        testTitle = testDoc.xpathEval("/item/title")[0].content        
        
        self.assertEqual(testTitle, title)
        
        description = doc.xpathEval("/item/description")[0].content
        testDescription = testDoc.xpathEval("/item/description")[0].content
        self.assertEqual(testDescription, description)
        
        # Test adding an empty entry, should get a ParseError        
        self.assertRaises(BaseDatabase.ParseError, self.db.addRecord, None, "")
        
        # Test adding an non-wellformed entry, should get a ParseError
        badEntry = "<document>"
        self.assertRaises(BaseDatabase.ParseError, self.db.addRecord, None, badEntry)
        
        # Test adding a None entry
        self.assertRaises(BaseDatabase.ParseError, self.db.addRecord, None, None)
        
        # Remove the test entry
        print "before"
        self.db.deleteRecord(None, id)
        print "after"
        # Add an entry pre-parsed
        doc = libxml2.parseDoc(testEntry)
        
        id = self.db.addRecord(None, doc)    
        self.assert_(id > 0)
        
        # Retrieve the entry we just added
        record = self.db.getRecord(None, id)
        
        # Compare it to the original document
        doc = libxml2.parseDoc(record)
        testDoc = libxml2.parseDoc(testEntry)
        
        title = doc.xpathEval("/item/title")[0].content        
        testTitle = testDoc.xpathEval("/item/title")[0].content        
        
        self.assertEqual(testTitle, title)
        
        description = doc.xpathEval("/item/description")[0].content
        testDescription = testDoc.xpathEval("/item/description")[0].content
        self.assertEqual(testDescription, description)
   
        # Remove the second test entry
        self.db.deleteRecord(None, id)
        
    def testGetRecord(self):
        # Add an entry
        id = self.db.addRecord(None, testEntry)
        
        # Test retrieving a non-existent record
        self.assertRaises(BaseDatabase.NotFoundError, self.db.getRecord, None, -1)
        
        # Remove the test entry
        self.db.deleteRecord(None, id)
        
    def testDeleteRecord(self):
        # Add an entry and the remove it
        id = self.db.addRecord(None, testEntry)    
        
        self.db.deleteRecord(None, id)
        
        # We shouldn't be able to find it now.
        self.assertRaises(BaseDatabase.NotFoundError, self.db.getRecord, None, id)
        
        # Test deleteing a non-existent entry
        self.assertRaises(BaseDatabase.NotFoundError, self.db.deleteRecord, None, -1)
        
        # Test cascading deletes.
        # add an item entry
        id = self.db.addRecord(None, "<item/>")  
        
        # add two comments that reference the item
        comment1 = self.db.addRecord(None, "<comment postID='" + str(id) + "'/>")    
        comment2 = self.db.addRecord(None, "<comment postID='" + str(id) + "'/>")    
        print "comment 1 " + str(comment1)
        print "comment 2 " + str(comment2)
        # Check to see if comment-count = 2 on the item entry tests increment
        # triggers
        entry = XMLFragment(self.db.getRecord(None, id))
        
        self.assertEqual(entry.getValue("/item/comment-count"), "2")
        
        # Add another comment and then remove it again to check proper counting
        comment3 = self.db.addRecord(None, "<comment postID='" + str(id) + "'/>")
        
        entry = XMLFragment(self.db.getRecord(None, id))
        # count should now be three
        self.assertEqual(entry.getValue("/item/comment-count"), "3") 
        # remove the comment and the count should drop back to two
        self.db.deleteRecord(None, comment3)
        entry = XMLFragment(self.db.getRecord(None, id))
        self.assertEqual(entry.getValue("/item/comment-count"), "2")
        
        # Deleting the item should also delete the comments.
        self.db.deleteRecord(None, id)
       
        self.assertRaises(BaseDatabase.NotFoundError, self.db.getRecord, None, id)
        self.assertRaises(BaseDatabase.NotFoundError, self.db.getRecord, None, comment1)
        self.assertRaises(BaseDatabase.NotFoundError, self.db.getRecord, None, comment2)
        
    def testUpdateRecord(self):
        # Add an entry and then change it
        id = self.db.addRecord(None, testEntry)    
        self.assert_(id > 0)

        record = self.db.getRecord(None, id)

        doc = libxml2.parseDoc(record)
        
        newTitle = "modified title"
        title = doc.xpathEval("/item/title")[0]
        title.setContent(newTitle)

        self.db.updateRecord(None, id, doc.serialize())
        
        # Make sure our change is really there
        record = self.db.getRecord(None, id)                
        doc = libxml2.parseDoc(record)
        
        title = doc.xpathEval("/item/title")[0].content
        self.assertEquals(title, newTitle)
        
        # Try updating with empty content
        self.assertRaises(BaseDatabase.ParseError, self.db.updateRecord, None, id, "")

        # Try updating with no content
        self.assertRaises(BaseDatabase.ParseError, self.db.updateRecord, None, id, None)
        
        self.db.deleteRecord(None, id)
    
    def testXPathQuery(self):
        id = self.db.addRecord(None, testEntryNs)    
        self.assert_(id > 0)
        
        result = self.db.xpathQuery(None, "/syncato:item/syncato:title")
        print result
        
        self.db.deleteRecord(None, id)
        
    def testDatabaseConfig(self): 
        config = self.db.dataConfig
        test = config.xpathEval("/datatypes/datatype[@root='comment']/admin-create")[0].content
        self.assertEquals(test, "no")


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDBXMLDatabase,'test'))
    #suite.addTest(unittest.makeSuite(TestFileDatabase,'test'))
    return suite
    
class TestFileDatabase(TestDatabase):
    def setUp(self):
        testConfig = """
            <blog>
                <db-type>file</db-type>
                <db-location>data/file-data</db-location>
                <cache-location>data/cache</cache-location>
                <user-style-location>stylesheets</user-style-location>   
                <system-style-location>stylesheets</system-style-location>    
                <ping-weblogs>no</ping-weblogs>
                <namespace prefix="syncato">http://www.syncato.org/NS/syncato</namespace>
            </blog>
        """
    
        config = libxml2.parseDoc(testConfig)
        self.db = Database(config)
    
class TestDBXMLDatabase(TestDatabase):
    def setUp(self):
        testConfig = """
            <blog>
                <db-type>dbxml2</db-type>
                <db-location>data/blog-data</db-location>
                <cache-location>data/cache</cache-location>
                <user-style-location>stylesheets</user-style-location>   
                <system-style-location>stylesheets</system-style-location>    
                <ping-weblogs>no</ping-weblogs>
                <namespace prefix="syncato">http://www.syncato.org/NS/syncato</namespace>
            </blog>
        """
    
        config = libxml2.parseDoc(testConfig)
        self.db = Database(config)
        
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
