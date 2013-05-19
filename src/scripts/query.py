#!/usr/local/bin/python

from bsddb3.db import *
from dbxml import *

import sys

container = XmlContainer(None, "../../data/blog-data/blog.dbxml")
container.open(None, DB_CREATE)

context = XmlQueryContext()
#context.setReturnType(XmlQueryContext.ResultValues)
query = sys.argv[1]
container.addIndex(None, "", "seconds", "node-attribute-equality-number")
indexes = container.getIndexSpecification(None)

for index in indexes:
    print index.get_name()
    print index.get_index()
from time import clock

container.setLogCategory(CATEGORY_ALL, True)
container.setLogLevel(LEVEL_DEBUG, True)

starttime = clock()
            
results = container.queryWithXPath(None, query, context)

print str(clock() - starttime) + " seconds"

#for result in results:
#    print result.asString()
        
#container.close()
