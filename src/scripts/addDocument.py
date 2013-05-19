#!/usr/bin/env python
#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.
#
# Adds a new document to the database

import libxml2
import sys

sys.path.append('lib')
import WeblogUtil
    
if (len(sys.argv) != 6):
    print "Usage: addDocument.py host baseURL username password content"
    sys.exit()
    
host = sys.argv[1]

base = sys.argv[2]

username = sys.argv[3]

password = sys.argv[4]

document = sys.argv[5]

content = open(document).read()
result = WeblogUtil.runRequest(host, username, password, "POST", base, content)
if (result.status == 201):
    print "Document URL: " + result.getheader("Location")
else:
    print str(result.status) + " " + result.reason
