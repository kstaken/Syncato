#!/usr/local/bin/python

import httplib, string
from base64 import encodestring

import libxml2
import sys, os
   
if (len(sys.argv) != 3):
    print "Usage: queryFiles.py query destination-dir"
    sys.exit()
    
query = sys.argv[1]

destination = sys.argv[2]

files = os.listdir(destination)

finalResult = []

finalResult.append("<results>")
for file in files:
    #print file
    doc = libxml2.parseFile(destination + "/" + file)
    results = doc.xpathEval(query)
    for item in results:
        finalResult.append(item.serialize())
    
finalResult.append("</results>")

print "".join(finalResult)

