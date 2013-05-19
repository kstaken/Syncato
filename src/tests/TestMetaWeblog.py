#!/usr/bin/env python
#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.

import xmlrpclib, string, unittest
import libxml2
from xmlrpclib import Boolean

title = "Test Post 1"
description = "Just a simple post to get started."
link = "http://www.example.com/post1"

#username and password
username = ''
password = ''

config = libxml2.parseFile("../../config/config.xml")
baseURL = config.xpathEval("/blog/base-url")[0].content
baseURL = string.replace(baseURL, "http://", "")
slash = baseURL.find('/')
host = baseURL[0:slash]
baseURL = baseURL[slash:]     
#figure out location of RPCServer
end = baseURL.split('/')
end[len(end)-1] = 'MetaWeblog'
RPCServer = 'http://' + host + string.join(end,'/')

testEntry = { 'title': title, 'description': description, 'link':link }

class TestMetaWeblog(unittest.TestCase):
    def setUp(self):
        self.server = xmlrpclib.Server(RPCServer)
        
    def testAddPost(self):
        """ test metaWeblog.addPost() """
        # add test entry
        post = self.server.metaWeblog.newPost("1", username, password, testEntry, 1)
        self.assert_(post.startswith("http://"))
        postID=post.split('http://' + host)[1]

        # clean up (delete test entry)
        result = self.server.metaWeblog.deletePost("1",postID,username,password,xmlrpclib.True)

        
    def testGetRecentPosts(self):
        """ test metaWeblog.getRecentPosts """
        numberOfPosts = 10
        
        result = self.server.metaWeblog.getRecentPosts("1", username, password, numberOfPosts)
        

    def testDeletePost(self):
        """ test metaWeblog.deletePost() """
        #add test entry
        post = self.server.metaWeblog.newPost("1", username, password, testEntry, 1)
        self.assert_(post.startswith("http://"))
        postID=post.split('http://' + host)[1]

        # clean up (delete test entry)
        result = self.server.metaWeblog.deletePost("1",postID,username,password,xmlrpclib.True)
        self.assertEqual(result, "OK")

    def testGetCategories(self):
        """ test metaWeblog.getCategories() """
        # just make sure this doesn't throw an exception
        result = self.server.metaWeblog.getCategories("1",username,password)


    def testGetUsersBlogs(self):
        """ test metaWeblog.getUsersBlogs() """
        return self.server.metaWeblog.getUsersBlogs("1",username,password)

    def testEditPost(self):
        """ test metaWeblog.editPost() """
        raise 'Not Implemented'

    def testGetPost(self):
        """ test metaWeblog.getPost() """
        # first create a post
        post = self.server.metaWeblog.newPost("1", username, password, testEntry, 1)
        self.assert_(post.startswith("http://"))
        postID=post.split('http://' + host)[1]

        # now get the post
        post = self.server.metaWeblog.getPost(postID, username, password)
        self.assertEqual(post['title'],testEntry['title'])
        self.assertEqual(post['description'],testEntry['description'])

        #clean up
        self.server.metaWeblog.deletePost("1", postID, username, password, 1)

class TestBlogger(unittest.TestCase):
    def setUp(self):
        self.server = xmlrpclib.Server(RPCServer)

    def testGetUsersBlogs(self):
        """ test blogger.getUsersBlogs() """
        return self.server.blogger.getUsersBlogs("1",username,password)

    def testNewPost(self):
        """ test blogger.addPost() """
        # add test entry
        post = self.server.blogger.newPost('1','1', username, password, testEntry, 1)
        self.assert_(post.startswith("http://"))
        postID=post.split('http://' + host)[1]

        # clean up (delete test entry)
        result = self.server.blogger.deletePost("1",postID,username,password,xmlrpclib.True)

    def testDeletePost(self):
        """ test blogger.deletePost() """
        post = self.server.blogger.newPost('1','1', username, password, testEntry, 1)
        self.assert_(post.startswith("http://"))
        postID=post.split('http://' + host)[1]

        # clean up (delete test entry)
        result = self.server.blogger.deletePost("1",postID,username,password,xmlrpclib.True)

        self.assertEqual(result,"OK")

    def testEditPost(self):
        """ test blogger.editPost() """
        #make a new post
        post = self.server.blogger.newPost('1','1', username, password, testEntry, 1)
        postID=post.split('http://' + host)[1]

        # get the post
        post = self.server.blogger.getPost('1',postID,username,password)
        post['description'] = "a new description"
        
        result = self.server.blogger.editPost('1',postID,username,password, post,1)
        self.assertEqual(result,"Reset Content")
        #now we fetch it again

        post = self.server.blogger.getPost('1',postID,username,password)
        self.assertEqual(post['description'],"a new description")

        # clean up
        self.server.blogger.deletePost('1',postID,username,password,1)
        
        
class TestMovableType(unittest.TestCase):
    def setUp(self):
        self.server = xmlrpclib.Server(RPCServer)

    def testGetPostCategories(self):
        """ test mt.getPostCategories """
        # create a test entry
        categories = ['XML',]
        testEntry = {'title': 'Test Entry', 'description': 'an entry to test with', 'categories': categories}
        post = self.server.metaWeblog.newPost("1",username,password,testEntry,1)
        postID = post.split('http://' + host)[1]

        # test
        categories = self.server.mt.getPostCategories(postID,'','')
        assert categories[0].has_key('categoryId')
        self.assertEqual(categories[0]['categoryName'], 'XML')

        # clean up
        result = self.server.metaWeblog.deletePost("1",postID,username,password,xmlrpclib.True)
    
    def testGetCategoryList(self):
        """ test mt.getCategoryList() """
        result = self.server.mt.getCategoryList("1",username,password)

        if result == Boolean(0):
            print 'there are no categies'

if __name__ == "__main__":
    unittest.main()
