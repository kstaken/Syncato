#!/usr/bin/python
#
# A simple script to edit entries in a Syncato site
#
# -- TextExtras User Script Info --
# %%%{TEName=Post XML To Inspriational Technology}%%%
# %%%{TEInput=AllText}%%%
# %%%{TEOutput=ReplaceAllText}%%%
# %%%{TEKeyEquivalent=~@x}%%%
# %%%{TEArgument=xmldatabases.conf}%%%
#
# %%%{TENewScript}%%%
# %%%{TEName=Post XML To Photo Blog}%%%
# %%%{TEInput=AllText}%%%
# %%%{TEOutput=ReplaceAllText}%%%
# %%%{TEKeyEquivalent=~@y}%%%
# %%%{TEArgument=photo.conf}%%%
#
# %%%{TENewScript}%%%
# %%%{TEName=Post XML To localhost}%%%
# %%%{TEInput=AllText}%%%
# %%%{TEOutput=ReplaceAllText}%%%
# %%%{TEKeyEquivalent=~@z}%%%
# %%%{TEArgument=localhost.conf}%%%

import os, sys
import httplib
from string import replace

import libxml2

sys.path.append("/Users/kstaken/Workspace/Book/Blog/dist/scripts/lib")

from WeblogClient import WeblogClient

# Configuration for where the weblog system is running. The config file is the 
# first argument to the script.
CONFIG_LOCATION = "/Users/kstaken/Workspace/Book/Blog"

config = libxml2.parseFile(CONFIG_LOCATION + "/" + sys.argv[1])

HOST = config.xpathEval("/blog/host")[0].content
# Username/password that has permission to post to the blog
USERNAME = config.xpathEval("/blog/user")[0].content
PASSWORD = config.xpathEval("/blog/password")[0].content

BASE_URL = "/WK/blog"

    
def encode(data):
    # replace any existing amp entities temporarily
    data = replace(data, '&amp;', '::amp::')
    
    # Replace bare &
    data = replace(data, '&', '&amp;')
    
    # Restore the original amp entities.
    data = replace(data, '::amp::', '&amp;')
    return data
    
def editPost(blog, postID, action):    
    # Skip the next blank line
    sys.stdin.readline()
    
    postBody = ""
    # Post body comes after this
    for line in sys.stdin.readlines():
        postBody = postBody + line
         
    postBody = encode(postBody)
    
    try:
        if (action.startswith("n")):
            postID = blog.addRawPost(postBody)
            postID = replace(postID, "http://" + HOST, "")
        else:
            blog.editRawPost(postID, postBody)
    except Exception, e:
        print "ERROR: " + str(e)
        
    # Setup the entry so that we can edit it again
    print "id:" + postID + " action:update\n"
    print postBody
    
def main():
    firstline = sys.stdin.readline()
    
    # Find the entryid and the action that is being executed
    actions = firstline.split(" ")
    postID = actions[0].split(":")[1]
    action = actions[1].split(":")[1].strip()
    
    blog = WeblogClient(HOST, BASE_URL, USERNAME, PASSWORD)
    
    # Determine what we should do
    if (action.startswith("g")):    
        post = blog.getRawPost(postID)
        
        # Setup the entry so that we can edit it again
        if (post):
            print "id:" + postID + " action:update\n"
            
            print post
        else:
            print "Not found"
    elif (action.startswith("d")):
        blog.deletePost(postID)
    elif (action.startswith("u") or action.startswith("n")):
        editPost(blog, postID, action)
    else:
        print "Unknown action"

main()    