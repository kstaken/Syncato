#!/usr/local/bin/python

import httplib, string
from base64 import encodestring

import libxml2
import sys

username = ''
password = ''

def runRequest(method, url, body = None):
    token = "Basic " + encodestring(username + ":" + password).strip()
    headers = {"Content-type": "text/xml", "Authorization": token}
    
    conn.request(method, url, body, headers)

    result = conn.getresponse()
        
    return result
    
if (len(sys.argv) != 4):
    print "Usage: db2Files.py host query destination-dir"
    sys.exit()
    
host = sys.argv[1]
conn = httplib.HTTPConnection(host)

query = sys.argv[2]

destination = sys.argv[3]

result = runRequest("GET", query)

content = result.read()
    
doc = libxml2.parseDoc(content)

results = doc.xpathEval("/results/node()")

for item in results:
    try:
         filename = item.xpathEval("@id")[0].content
         
         file = open(destination + "/" + filename + ".xml", "w")
         file.write(item.serialize())
    except:
        # skip it if there is an error. 
        pass

