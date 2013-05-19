#!/usr/local/bin/python
#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.
#
# Adds a new document to the database

import libxml2
import sys, re

sys.path.append('lib')
import WeblogUtil
    
if (len(sys.argv) != 6):
    print "Usage: blacklist2xml.py host baseURL username password blacklist"
    sys.exit()
    
host = sys.argv[1]

base = sys.argv[2]

username = sys.argv[3]

password = sys.argv[4]

file = sys.argv[5]

content = open(file).read()
lines = content.split("\n")
for line in lines: 
    empty = re.compile(r"^\s*$")
    if (not(line.startswith("#") or empty.match(line))):
        doc = libxml2.newDoc("1.0")

        root = doc.newChild(None, "blacklist", None)
        
        root.newChild(None, "url", line)
        
        content = doc.serialize()
    
        result = WeblogUtil.runRequest(host, username, password, "POST", base, content)
        if (result.status == 201):
            print "Document URL: " + result.getheader("Location")
        else:
            print result.status + " " + result.reason
