#!/usr/bin/python
#
# A simple script to edit entries in a Syncato site
#
# -- TextExtras User Script Info --
# %%%{TEName=Post To Inspriational Technology}%%%
# %%%{TEInput=AllText}%%%
# %%%{TEOutput=ReplaceAllText}%%%
# %%%{TEKeyEquivalent=~@p}%%%
# %%%{TEArgument=xmldatabases.conf}%%%
#
# %%%{TENewScript}%%%
# %%%{TEName=Post To Photo Blog}%%%
# %%%{TEInput=AllText}%%%
# %%%{TEOutput=ReplaceAllText}%%%
# %%%{TEKeyEquivalent=~@c}%%%
# %%%{TEArgument=photo.conf}%%%
#
# %%%{TENewScript}%%%
# %%%{TEName=Post To localhost}%%%
# %%%{TEInput=AllText}%%%
# %%%{TEOutput=ReplaceAllText}%%%
# %%%{TEKeyEquivalent=~@t}%%%
# %%%{TEArgument=localhost.conf}%%%

import os, sys
import httplib
from string import replace
import StringIO

import libxml2

sys.path.append("/Users/kstaken/Workspace/Book/Blog/dist/scripts/lib")
sys.path.append("/Users/kstaken/Workspace/Book/Blog/client/rhizml")

import rhizml

from WeblogClient import WeblogClient

# Configuration for where the weblog system is running. The config file is the 
# first argument to the script.
CONFIG_LOCATION = "/Users/kstaken/Workspace/Book/Blog"

config = libxml2.parseFile(CONFIG_LOCATION + "/" + sys.argv[1])

HOST = config.xpathEval("/blog/host")[0].content
# Username/password that has permission to post to the blog
USERNAME = config.xpathEval("/blog/user")[0].content
PASSWORD = config.xpathEval("/blog/password")[0].content

BASE_URL =  config.xpathEval("/blog/base-url")[0].content

    
def encode(data):
    # replace any existing amp entities temporarily
    data = replace(data, '&amp;', '::amp::')
    
    # Replace bare &
    data = replace(data, '&', '&amp;')
    
    # Restore the original amp entities.
    data = replace(data, '::amp::', '&amp;')
    return data
    
def editPost(blog, postID, action, format):
    # There should be a blank line and then the title
    titleline = sys.stdin.readline()
    titleline = sys.stdin.readline()
    
    postTitle = encode(titleline.split(":")[1].strip())
    
    # categories should be on the next line
    catline = encode(sys.stdin.readline())
    
    categoryList = catline.split(":")[1].strip()
    categories = categoryList.split(",")
    
    # Skip the next blank line
    sys.stdin.readline()
    
    postBody = ""
    # Post body comes after this
    for line in sys.stdin.readlines():
        postBody = postBody + line
         
    postBodyPre = postBody
    if (format == "rz"):
        postBody = rhizml.rhizml2xml(StringIO.StringIO(postBody), prettyprint=True)
    else:
        postBody = encode(postBody)
    
    try:
        if (action.startswith("n")):
            postID = blog.addPost(postTitle, postBody, categories)
            postID = replace(postID, "http://" + HOST, "")
        else:
            blog.editPost(postID, postTitle, postBody, categories)
    except Exception, e:
        print "ERROR: " + str(e)
        
    # Setup the entry so that we can edit it again
    print "id:" + postID + " action:update format:" + format + "\n"
    print "title: " + postTitle
    print "category: " + ",".join(categories)
    print ""
    print postBodyPre
    
def main():
    firstline = sys.stdin.readline()
    
    # Find the entryid and the action that is being executed
    actions = firstline.split(" ")
    postID = actions[0].split(":")[1]
    action = actions[1].split(":")[1].strip()
    try:
        format = actions[2].split(":")[1].strip()
    except:
        format = ""
    
    blog = WeblogClient(HOST, BASE_URL, USERNAME, PASSWORD)
    
    # Determine what we should do
    if (action.startswith("g")):    
        post = blog.getPost(postID)
        
        # Setup the entry so that we can edit it again
        if (post):
            print "id:" + postID + " action:update\n"
            print "title: " + post["title"]
            
            categories = post["categories"]      
            print "category: " + ", ".join(categories)
            print ""
            
            print post["body"]
        else:
            print "Not found"
    elif (action.startswith("d")):
        blog.deletePost(postID)
    elif (action.startswith("u") or action.startswith("n")):
        editPost(blog, postID, action, format)
    else:
        print "Unknown action"

main()    