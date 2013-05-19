#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.

import httplib
from base64 import encodestring
from string import replace

def runRequest(host, username, password, method, url, body = None):
    conn = httplib.HTTPConnection(host)

    token = "Basic " + encodestring(username + ":" + password).strip()
    headers = {"Content-type": "text/xml", "Authorization": token}
    
    conn.request(method, url, body, headers)

    result = conn.getresponse()
        
    return result
    
def encode(data):
    data = replace(data, '&', '&amp;')
    data = replace(data, '<', '&lt;')
    data = replace(data, '>', '&gt;')
    data = replace(data, '"', '&quot;')
    data = replace(data, "'", '&apos;')
    return data
    
def decode(data):
    data = replace(data, '&lt;', '<')
    data = replace(data, '&gt;', '>')
    data = replace(data, '&quot;', '"')
    data = replace(data, '&apos;', "'")
    data = replace(data, '&amp;', '&')    
    return data
    
def configValue(config, xpath, default=""):
    results = config.xpathEval(xpath)
    if (len(results) > 0):
        return results[0].content
    else:
        return default