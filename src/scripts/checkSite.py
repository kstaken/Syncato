#!/usr/local/bin/python
#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.

import httplib, os, smtplib, time

url = "/WK/blog"

conn = httplib.HTTPConnection("www.staken.org")
conn.request("GET", url)

result = conn.getresponse()
if (result.status == 500):
    smtp = smtplib.SMTP("www.xmldatabases.org")
    #smtp = smtplib.SMTP("smtp.west.cox.net")
    
    message = """Subject: Server down, restarting
    
    """
    smtp.sendmail("kstaken@xmldatabases.org", ["kstaken@xmldatabases.org"], message + time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()))
    
    os.system("/etc/init.d/webkit restart")
    print "failed " + chr(7)
