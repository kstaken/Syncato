#!/usr/bin/env python

from bsddb3.db import *
from dbxml import *

import libxml2
import sys

environment = DBEnv()
environment.open("../../data/blog-data", DB_CREATE|DB_INIT_LOCK|DB_INIT_LOG|DB_INIT_MPOOL|DB_INIT_TXN, 0)

# Open the main database
db = XmlContainer(environment, "blog.dbxml")

db.open(None, DB_CREATE)

#container = XmlContainer(None, "../../data/blog-data/cache.dbxml")
#container.open(None, DB_CREATE)

context = XmlQueryContext()
context.setReturnType(XmlQueryContext.ResultValues)
query = sys.argv[1]

for i in range(1, 1000):
    db.queryWithXPath(None, query, context)
          
#db.close()
#environment.close()
