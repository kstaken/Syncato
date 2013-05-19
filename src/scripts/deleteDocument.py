#!/usr/bin/env python
#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.

import sys

sys.path.append('lib')
import WeblogUtil
    
if (len(sys.argv) != 6):
    print "Usage: deleteDocument.py host baseURL username password documentID"
    sys.exit()
    
host = sys.argv[1]

base = sys.argv[2]

username = sys.argv[3]

password = sys.argv[4]

documentID = sys.argv[5]

result = WeblogUtil.runRequest(host, username, password, "DELETE", base + "/" + documentID)
if (result.status == 200):
    print "Document removed"
else:
    print result.status + " " + result.reason
    
