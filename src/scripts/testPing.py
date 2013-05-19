#!/usr/local/bin/python
import xmlrpclib
import libxml2

config = libxml2.parseFile("../config/config.xml")

def configValue(xpath):
    return config.getRootElement().xpathEval(xpath)[0].content
        
# ping weblogs.com
server = xmlrpclib.Server('http://rpc.weblogs.com/RPC2')

server.weblogUpdates.ping(configValue("/blog/title"), configValue("/blog/base-url"))

# Ping blog.gs
server = xmlrpclib.Server('http://ping.blo.gs/')

server.weblogUpdates.ping(configValue("/blog/title"), configValue("/blog/base-url"))

