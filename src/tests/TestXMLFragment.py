#!/usr/bin/env python
# Unit tests for the XMLFragment module.
import sys
sys.path.append('../lib')

from XMLFragment import *

import libxml2
import unittest, os
        
testEntry = """<item>
    <title>Test Post 1</title>
    <description>Just a simple post to get started.</description>
    <category>XML</category>
    <category>Java</category>
</item>
"""

class TestXMLFragment(unittest.TestCase):
    def setUp(self):
        namespaces = """
            <root>
                <namespace prefix="t">test</namespace>
                <namespace prefix="s">test2</namespace>
            </root>
        """
        config = libxml2.parseDoc(namespaces)
        registerNamespaces(config.xpathEval("/root/namespace"))
        
    def testAddNode(self):
        # Test creating a new document
        doc = XMLFragment()
        
        doc.addNode("/root")
        
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<root/>\n')
        
        # Test adding on a child node
        doc.addNode("/root/child")
        
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<root><child/></root>\n')
        
        # Test creating the parent and child in one step.                
        doc = XMLFragment()
        doc.addNode("/root/child")
        
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<root><child/></root>\n')
        
        # Test creating the parent and child in one step with some content               
        doc = XMLFragment()
        doc.addNode("/root/child", "text")
        
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<root><child>text</child></root>\n')
        
        # Now add another level
        doc.addNode("/root/child/subchild")
        
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<root><child>text<subchild/></child></root>\n')
        
        # Add a second child with the same name
        doc.addNode("/root/child", "text")
        
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<root><child>text<subchild/></child><child>text</child></root>\n')
        
        # Create two children then add a subchild to each
        doc = XMLFragment()
        doc.addNode("/root/child")
        doc.addNode("/root/child")
        doc.addNode("/root/child/subchild")
        
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<root><child><subchild/></child><child><subchild/></child></root>\n')
        
        # Create two children then add a subchild to just the second child
        doc = XMLFragment()
        doc.addNode("/root/child")
        doc.addNode("/root/child")
        doc.addNode("/root/child[2]/subchild")
        
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<root><child/><child><subchild/></child></root>\n')
        
        # Test adding with an anonymouse root node
        doc = XMLFragment()
        doc.addNode("/root/child")
        doc.addNode("/node()/child")
        doc.addNode("/node()/child[2]/subchild")
        
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<root><child/><child><subchild/></child></root>\n')
        
        # add an attribute to the first child
        doc.addNode("/root/child[1]/@attr", "text")
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<root><child attr="text"/><child><subchild/></child></root>\n')
        
        # add a string that should be parsed as markup
        doc = XMLFragment()
        doc.addNode("/root/child")
        doc.addNode("/root/markup", "<test>text</test>", 1)
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<root><child/><markup><test>text</test></markup></root>\n')
       
        # add a pre-parsed node to the document
        doc = XMLFragment()
        doc.addNode("/root/child")
        markup = libxml2.parseDoc("<test>text</test>")
        doc.addNode("/root/markup", markup.getRootElement())
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<root><child/><markup><test>text</test></markup></root>\n')
        
    def testAddNodeNs(self):        
        # Check creating the root in a namespace                
        doc = XMLFragment()
        #doc.registerNamespaces(namespaces)
        doc.addNode("/t:root")
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<t:root xmlns:t="test"/>\n')
        
        # now add a child in the same namespace
        doc.addNode("/t:root/t:child")
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<t:root xmlns:t="test"><t:child/></t:root>\n')
        
        # now add a child in no namespace
        doc.addNode("/t:root/child")
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<t:root xmlns:t="test"><t:child/><child/></t:root>\n')
        
        # now add a child in a different namespace
        doc.addNode("/t:root/child/s:child")
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<t:root xmlns:t="test"><t:child/><child xmlns:s="test2"><s:child/></child></t:root>\n')
        
        # Check creating the root in a namespace with some content               
        doc = XMLFragment()
        #doc.registerNamespaces(namespaces)
        doc.addNode("/t:root", "test")
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<t:root xmlns:t="test">test</t:root>\n')
        
        # Now add a node with no NS and some content
        doc.addNode("/t:root/child", "test")
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<t:root xmlns:t="test">test<child>test</child></t:root>\n')
        
        # Now add some markup that doesn't have any namespaces
        doc.addNode("/t:root/child/markup", "some <b>content</b> bold", 1)
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<t:root xmlns:t="test">test<child>test<markup>some <b>content</b> bold</markup></child></t:root>\n')
        
        # Test combinations of namespaces in markup
        
        # Add some markup to a node in a namespace but where the markup has no 
        # namespaces
        doc = XMLFragment()
        #doc.registerNamespaces(namespaces)
        doc.addNode("/t:root")        
        doc.addNode("/t:root/s:markup", "some <b>content</b> bold", 1)
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<t:root xmlns:t="test" xmlns:s="test2"><s:markup>some <b>content</b> bold</s:markup></t:root>\n')
        
        # Add markup that uses namespaces
        doc = XMLFragment()
        #doc.registerNamespaces(namespaces)
        doc.addNode("/t:root")        
        doc.addNode("/t:root/s:markup", "some <x:b xmlns:x='test3'>content</x:b> bold", 1)
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<t:root xmlns:t="test" xmlns:s="test2"><s:markup>some <x:b xmlns:x="test3">content</x:b> bold</s:markup></t:root>\n')       
        
        # Test creation of a deeper tree to make sure we get the proper ns defs
        doc = XMLFragment()
        #doc.registerNamespaces(namespaces)
        doc.addNode("/t:root/t:child/t:child", "test")        
        doc.addNode("/t:root/t:child")
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<t:root xmlns:t="test"><t:child><t:child>test</t:child></t:child><t:child/></t:root>\n')       
        
    def testUpdateNode(self):
        # create a tree and then set a node to a new value
        doc = XMLFragment()
        doc.addNode("/root/child")
        doc.updateNode("/root/child", "text")
        
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<root><child>text</child></root>\n')
        
        # add another child and then update both to the same value
        doc.addNode("/root/child")
        doc.updateNode("/root/child", "newText")
        
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<root><child>newText</child><child>newText</child></root>\n')
        
        # Now just update the second child.
        doc.updateNode("/root/child[2]", "text")
        
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<root><child>newText</child><child>text</child></root>\n')
        
        # Now update an attribute
        doc.addNode("/root/child[1]/@attr", "text")
        doc.updateNode("/root/child[1]/@attr", "newText")
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<root><child attr="newText">newText</child><child>text</child></root>\n')
        
        # change a node to a string that should be parsed as markup
        doc = XMLFragment()
        doc.addNode("/root/child", "text")
        doc.updateNode("/root/child", "<test>text</test>", 1)
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<root><child><test>text</test></child></root>\n')
        
        # replace the content of a node with more then one child
        doc = XMLFragment()
        doc.addNode("/root/child", "<test>text</test><test>text2</test>", 1)
        doc.updateNode("/root/child", "<test>text3</test><test>text4</test>", 1)
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<root><child><test>text3</test><test>text4</test></child></root>\n')
       
        # add a pre-parsed node to the document
        doc = XMLFragment()
        doc.addNode("/root/child")
        markup = libxml2.parseDoc("<test>text</test>")
        doc.updateNode("/root/child", markup.getRootElement())
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<root><child><test>text</test></child></root>\n')
  
        # Update a node that doesn't already exist.
        doc = XMLFragment()
        markup = libxml2.parseDoc("<test>text</test>")
        doc.updateNode("/root/child", markup.getRootElement())
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<root><child><test>text</test></child></root>\n')
  
    def testUpdateNodeNs(self):
        pass
        
    def testRemoveNode(self):
        # create a tree then remove the child
        doc = XMLFragment()
        doc.addNode("/root/child")
        doc.removeNode("/root/child")
        
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<root/>\n')
        
        # create a tree then remove the second child
        doc = XMLFragment()
        doc.addNode("/root/child")
        doc.addNode("/root/child")
        doc.removeNode("/root/child[2]")
        
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<root><child/></root>\n')
        
        # Test removing attributes
    def testRemoveNodeNs(self):
        namespaces = {'t': "test", 's': "test2"}
        
        # Test deleting a node that's in a namespace                
        doc = XMLFragment()
        #doc.registerNamespaces(namespaces)
        
        doc.addNode("/root/t:child")
        doc.removeNode("/root/t:child")
        
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<root xmlns:t="test"/>\n')
        
        # create a tree then remove the second child
        doc = XMLFragment()
        #doc.registerNamespaces(namespaces)
        
        doc.addNode("/root/t:child")
        doc.addNode("/root/t:child")
        doc.removeNode("/root/t:child[2]")
        
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<root xmlns:t="test"><t:child/></root>\n')
        
    def testInsertNodeBefore(self):
        # create a tree and then insert a new empty node
        doc = XMLFragment()
        doc.addNode("/root/child")
        doc.insertNodeBefore("/root/child", "newChild")
        
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<root><newChild/><child/></root>\n')
        
        # create a tree and then insert a new node with content
        doc = XMLFragment()
        doc.addNode("/root/child")
        doc.insertNodeBefore("/root/child", "newChild", "text")
        
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<root><newChild>text</newChild><child/></root>\n')
  
        # create a tree and then insert a new node with markup content
        doc = XMLFragment()
        doc.addNode("/root/child")
        doc.insertNodeBefore("/root/child", "newChild", "<b>text</b>", 1)
        
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<root><newChild><b>text</b></newChild><child/></root>\n')
  
    def testInsertNodeAfter(self):
        # create a tree and then insert a new empty node
        doc = XMLFragment()
        doc.addNode("/root/child")
        doc.insertNodeAfter("/root/child", "newChild")
        
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<root><child/><newChild/></root>\n')
        
        # create a tree and then insert a new node with content
        doc = XMLFragment()
        doc.addNode("/root/child")
        doc.insertNodeAfter("/root/child", "newChild", "text")
        
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<root><child/><newChild>text</newChild></root>\n')
        
        # create a tree and then insert a new node with markup content
        doc = XMLFragment()
        doc.addNode("/root/child")
        doc.insertNodeAfter("/root/child", "newChild", "<b>text</b>", 1)
        
        self.assertEqual(doc.serialize(), '<?xml version="1.0"?>\n<root><child/><newChild><b>text</b></newChild></root>\n')
  
    def testGetValue(self):
        fragment = XMLFragment(testEntry)
        
        self.assertEqual(fragment.getValue("/item/title"), "Test Post 1")
        self.assertEqual(fragment.getValue("/item/category"), "XML")
        self.assertEqual(fragment.getValue("/item/category", "default"), "XML")
        self.assertEqual(fragment.getValue("/item/no-exist"), "")
        self.assertEqual(fragment.getValue("/item/no-exist", "default"), "default")
        
        # Test relative paths against nodes
        fragment2 = fragment.getSingle("/item")
        self.assertEqual(fragment2.getValue("title"), "Test Post 1")
        self.assertEqual(fragment2.getValue("category"), "XML")
        self.assertEqual(fragment2.getValue("no-exist", "default"), "default")
        
    def testGetSingle(self):
        doc = libxml2.parseDoc(testEntry)
        
        fragment = XMLFragment(doc)
        
        self.assertEqual(fragment.getSingle("/item/title").getFragment().content, "Test Post 1")
        self.assertEqual(fragment.getSingle("/item/category").getFragment().content, "XML")
        self.assertEqual(fragment.getSingle("/item/no-exist"), None)

if __name__ == '__main__':
    unittest.main()