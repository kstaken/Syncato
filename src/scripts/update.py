#!/usr/local/bin/python
#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.

from string import replace
import libxml2
import sys

sys.path.append('lib')
import WeblogUtil
         
if (len(sys.argv) != 5):
    print "Usage: update.py host baseURL username passwd"
    sys.exit()
    
host = sys.argv[1]
base = sys.argv[2]

username = sys.argv[3]

password = sys.argv[4]

query =  base + "/category"
result = WeblogUtil.runRequest(host, username, password, "GET", query)

content = result.read()

doc = libxml2.parseDoc(content)

results = doc.xpathEval("/results/node()")

for item in results:
    try:
        documentID = item.xpathEval("@id")[0].content
        print documentID
        content = item.serialize()
        content = replace(content, "<category", "<category-def")
        content = replace(content, "</category", "</category-def")
        print content
        result = WeblogUtil.runRequest(host, username, password, "POST", base + "/" + documentID, content)
        
    except:
        # skip it if there is an error. 
        pass

