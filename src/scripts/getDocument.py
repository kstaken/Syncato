#!/usr/local/bin/python
#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.

import libxml2
import sys

sys.path.append('lib')
import WeblogUtil
    
if (len(sys.argv) != 6):
    print "Usage: getDocument.py host baseURL username password documentID"
    sys.exit()
    
host = sys.argv[1]

base = sys.argv[2]

username = sys.argv[3]

password = sys.argv[4]

documentID = sys.argv[5]

result = WeblogUtil.runRequest(host, username, password, "GET", base + "/" + documentID)
if (result.status == 200):
    print result.read()
else:
    print result.status + " " + result.reason
    
