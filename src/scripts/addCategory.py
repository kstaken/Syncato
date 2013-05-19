#!/usr/bin/env python
#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.
#
# Adds a new category to the database.
#
# Usage: addCategory.py categoryID categoryTitle categoryDescription

import libxml2
import sys

sys.path.append('lib')
import WeblogUtil

if (len(sys.argv) != 7):
    print "Usage: addCategory.py host baseURL username password categoryTitle categoryDescription"
    sys.exit() 
    
doc = libxml2.newDoc("1.0")

root = doc.newChild(None, "category-def", None)

root.newChild(None, "title", sys.argv[5])
root.newChild(None, "description", sys.argv[6])

print doc.serialize()

    
host = sys.argv[1]
base = sys.argv[2]
username = sys.argv[3]
password = sys.argv[4] 

content = doc.serialize()

result = WeblogUtil.runRequest(host, username, password, "POST", base, content)
if (result.status == 201):
    print "Category URL: " + result.getheader("Location")
else:
    print result.status + " " + result.reason
