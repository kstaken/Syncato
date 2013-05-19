#!/usr/bin/env python
#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.
# 
# Imports a set of records from an XML file
#
# The records are broken up by an XPath query that selects the individual 
# entries to insert.
#
# Usage: importData.py file xpath

from bsddb3.db import *
from dbxml import *

import libxml2
import sys

environment = DBEnv()
environment.open("../../data/blog-data", DB_CREATE|DB_INIT_LOCK|DB_INIT_LOG|DB_INIT_MPOOL|DB_INIT_TXN, 0)

# Open the main database
db = XmlContainer(environment, "blog.dbxml")
db.open(None, DB_CREATE)
db.addIndex(None, "", "pubDate/seconds", "edge-attribute-equality-number")

doc = libxml2.parseFile(sys.argv[1])

results = doc.xpathEval(sys.argv[2])
for result in results:
    print result.serialize()
    try:
        doc = libxml2.parseDoc(result.serialize())
        document = XmlDocument()
        document.setContent(result.serialize())
        db.putDocument(None, document)
    except:
        print "Failed on " + result.serialize()
        
db.close()
environment.close()        
