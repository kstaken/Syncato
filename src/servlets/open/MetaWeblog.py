#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.
#  
# $Id: MetaWeblog.py,v 1.6 2003/11/25 06:00:54 kstaken Exp $
import sys, string, traceback, os, httplib, time, re

try:
    from xmlrpclib import xmlrpclib
except ImportError:
    import xmlrpclib

from xmlrpclib import Boolean

import libxml2

from WebKit.XMLRPCServlet import XMLRPCServlet
from WebKit.XMLRPCServlet import _getXmlDeclAttr

import WeblogClient

ONE_WEEK = 60 * 60 *  24 * 7;

class MetaWeblog(XMLRPCServlet):
    """
    Implementation of the MetaWeblog and Blogger APIs.
    """

    def __init__(self):
        XMLRPCServlet.__init__(self)
        self.config = libxml2.parseFile("../config/config.xml")
        baseURL = self.config.xpathEval("/blog/base-url")[0].content
        baseURL = string.replace(baseURL, "http://", "")
        slash = baseURL.find('/')
        self.host = baseURL[0:slash]
        self.baseURL = baseURL[slash:]     

    def exposedMethods(self):
        bloggerMethods = ['blogger_getUsersBlogs', 'blogger_deletePost', 'blogger_getRecentPosts', \
                          'blogger_newPost',  'blogger_editPost', 'blogger_getPost']
        metaWeblogMethods = ['metaWeblog_newPost', 'metaWeblog_editPost', 'metaWeblog_getPost', \
            'metaWeblog_getRecentPosts', 'metaWeblog_getUsersBlogs', 'metaWeblog_getCategories', \
            'metaWeblog_deletePost' ]
        movableTypeMethods = ['mt_getPostCategories', 'mt_setPostCategories', 'mt_getCategoryList', 'mt_publishPost']

        return bloggerMethods + metaWeblogMethods + movableTypeMethods

    def runRequest(self, method, url, body = None):
        conn = httplib.HTTPConnection(self.host)
        headers = {"Content-type": "text/xml" }

        conn.request(method, url, body, headers)

        result = conn.getresponse()

        return result

    def metaWeblog_newPost(self, blogId, username, password, content, publish):
        client = WeblogClient.WeblogClient(self.host, self.baseURL, username, password)

        categories = []
        if (content.has_key("categories")):
           categories = content['categories']
        postID = client.addPost(content['title'], content['description'], categories)

        if (postID == ""):
            raise "Unable to post new entry"

        return postID

    def blogger_newPost(self,appkey,blogId,username,password,content,publish):
        # wrap metaWeblog_newPost(). drop appkey
        return self.metaWeblog_newPost(blogId,username,password,content,publish)
    

    def metaWeblog_editPost(self, postID, username, password, content, publish):
        client = WeblogClient.WeblogClient(self.host, self.baseURL, username, password)

        categories = []
        if (content.has_key("categories")):
           categories = content['categories']

        result = client.editPost(postID, content['title'], content['description'], categories)

        return result.reason
    
    def blogger_editPost(self, appkey, postID, username, password, content, publish):
        # 
        client = WeblogClient.WeblogClient(self.host, self.baseURL, username, password)

        categories = []

        result = client.editPost(postID, content['title'], content['description'], categories)
        return result.reason

    def metaWeblog_getPost(self, postID, username, password):
        client = WeblogClient.WeblogClient(self.host, self.baseURL, username, password)

        result = client.getPost(postID)
        
        finalResult = {}
        finalResult['postid'] = postID
        finalResult['title'] = result['title']
        finalResult['description'] = result['body']
        
        finalResult['categories'] = result['categories']
        return finalResult

    def blogger_getPost(self, appkey, postID, username, password):
        # wrap metaWeblog_getPost
        return self.metaWeblog_getPost(postID, username, password)

    def metaWeblog_getRecentPosts(self, blogId, username, password, numberOfPosts):
        posts = []
        client = WeblogClient.WeblogClient(self.host, self.baseURL, username, password)

        itemRoot = self.config.xpathEval("/blog/post-root-element")[0].content 
        query = "/" + itemRoot + "[pubDate/@seconds > " + str(time.time() - ONE_WEEK) + "]"

        result = client.runRequest("GET", self.baseURL + query)

        recentRSS = libxml2.parseDoc(result.read())

        results = recentRSS.xpathEval('/results/item')
        for item in results:
            entry = {} 

            entry['title'] = item.xpathEval('title')[0].content
            entry['postid'] = self.baseURL + "/" + item.xpathEval('@id')[0].content

            body = item.xpathEval('description')[0].serialize(format = 1)             
            body = re.sub("^<description>", "", body)
            body = re.sub("</description>$", "", body)

            entry['description'] = body
            cats = item.xpathEval('category')
            entry['categories'] = []
            for cat in cats:
                entry['categories'].append(cat.content)
                
            posts.append(entry)

        return posts

    def blogger_getRecentPosts(self, appkey, blogid, username, password, numberOfPosts):
        # wrap metaWeblog_getRecentPosts. drop appkey
        return self.metaWeblog_getRecentPosts(blogid, username, password, numberOfPosts)
        
    def metaWeblog_deletePost(self, appkey, postID, username, password, publish):
        client = WeblogClient.WeblogClient(self.host, self.baseURL, username, password)
        print "post to delete:", postID
        result = client.deletePost(postID)
        return result.reason

    def blogger_deletePost(self,appkey,postID,username,password,publish):
        # just a wrapper for metaWeblog_deletePost.
        return self.metaWeblog_deletePost(appkey,postID,username,password,publish)

    def mt_getCategoryList(self, blogid, username, password):
        categories = []
        client = WeblogClient.WeblogClient(self.host, self.baseURL, username, password)
        
        itemRoot = self.config.xpathEval("blog/category-root-element")[0].content
        query = "/" + itemRoot
        
        result = client.runRequest("GET", self.baseURL + query)
    
        categoryXML = libxml2.parseDoc(result.read())
        results = categoryXML.xpathEval('//category')
        #print results
        for item in results:
            category = {}
            
            category['categoryId'] = item.xpathEval('@id')[0].content
            category['categoryName'] = item.xpathEval('title')[0].content
            # metaweblog API defines htmlUrl and rssUrl that we don't have(?)
            #category['htmlUrl'] = item.xpathEval('htmlUrl')[0].content
            #category['rssUrl'] = item.xpathEval('rssUrl')[0].content
    
            categories.append(category)
    
        if (len(categories) > 0 ):
            return categories
        else:
            return Boolean(0)

    def metaWeblog_getCategories(self, blogid, username, password):
        categories = {}
        client = WeblogClient.WeblogClient(self.host, self.baseURL, username, password)
        
        itemRoot = self.config.xpathEval("blog/category-root-element")[0].content
        query = "/" + itemRoot
        
        result = client.runRequest("GET", self.baseURL + query)
    
        categoryXML = libxml2.parseDoc(result.read())
        results = categoryXML.xpathEval('//category-def')
        
        for item in results:
            category = {}
            title = item.xpathEval('title')[0].content
            category['id'] = item.xpathEval('@id')[0].content
            category['description'] = title
            # metaweblog API defines htmlUrl and rssUrl that we don't have(?)
            #category['htmlUrl'] = item.xpathEval('title')[0].content
            #category['rssUrl'] = item.xpathEval('title')[0].content
    
            categories[title] = category
    
        return categories


    def mt_getPostCategories(self, postID, username, password):
        client = WeblogClient.WeblogClient(self.host, self.baseURL, username, password)
        print postID
        result = client.getPost(postID)
        print result
        categories = result['categories']
        finalResult = []
        for category in categories:
            print category
            rec = {}
            rec['categoryId'] = category
            rec['categoryName'] = category
            rec['isPrimary']= Boolean(0)
            finalResult.append(rec)

        return finalResult 

    def mt_setPostCategories(self, postID, username, password, categories=[]):
        return Boolean(1)

    def mt_publishPost(self, postID, username, password):
        return Boolean(1)

    def publishPost(self, postID, username, password):
        # We don't support this concept so we just return true.
        return Boolean(1)

    # We don't actually care about these methods.    
    def getTemplate(self, appkey, blogid, username, password, templateType):
        return ""

    def setTemplate(self, appkey, blogid, username, password, template, templateType):
        return Boolean(1)

    def metaWeblog_getUsersBlogs(self, appkey, username, password):
        # this could probably be changed to return a reasonable default
        return [{ 'url': 'http://myblog', 'blogid': 'id', 'blogName': 'my blog' }]

    def blogger_getUsersBlogs(self,appkey,username,password):
        # wrap the metaWeblog implemenetation
        return self.metaWeblog_getUsersBlogs(appkey,username,password)
    

    def metaWeblog_newMediaObject(self, blogid, username, password, struct):
        return {}

    # Reimplementation from XMLRPCServlet to enable the metaweblog.name convention
    def respondToPost(self, transaction):
        """
        This is similar to the xmlrpcserver.py example from the xmlrpc
        library distribution, only it's been adapted to work within a
        WebKit servlet.
        """
        try:
            # get arguments
            data = transaction.request().rawInput(rewind=1).read()
            encoding = _getXmlDeclAttr(data, "encoding")
            params, method = xmlrpclib.loads(data)

            # build the appropriate method call
            prefix,method = method.split(".")
            method = prefix + "_" + method
            
            # generate response
            try:
                # This first test helps us to support PythonWin, which uses
                # repeated calls to __methods__.__getitem__ to determine the
                # allowed methods of an object.
                if method == '__methods__.__getitem__':
                    response = self.exposedMethods()[params[0]]
                else:
                    response = self.call(method, *params)
                if type(response) != type(()):
                    response = (response,)
            except Exception, e:
                fault = self.resultForException(e, transaction)
                response = xmlrpclib.dumps(xmlrpclib.Fault(1, fault), encoding=encoding)
                self.sendOK('text/xml', response, transaction)
                self.handleException(transaction)
            except:  # if it's a string exception, this gets triggered
                fault = self.resultForException(sys.exc_info()[0], transaction)
                response = xmlrpclib.dumps(xmlrpclib.Fault(1, fault), encoding=encoding)
                self.sendOK('text/xml', response, transaction)
                self.handleException(transaction)
            else:                
                response = xmlrpclib.dumps(response, methodresponse=1, encoding=encoding)
                self.sendOK('text/xml', response, transaction)
        except:
            # internal error, report as HTTP server error
            print 'XMLRPCServlet internal error'
            print string.join(traceback.format_exception(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2]))
            transaction.response().setStatus(500, 'Server Error')
            self.handleException(transaction)

def encode(data):
    data = string.replace(data, '&', '&amp;')
    data = string.replace(data, '<', '&lt;')
    data = string.replace(data, '>', '&gt;')
    data = string.replace(data, '"', '&quot;')
    data = string.replace(data, "'", '&apos;')
    return data
             
