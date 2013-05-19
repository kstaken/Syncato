#!/usr/local/bin/python
#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.
#  
# $Id: Database.py,v 1.5 2003/12/15 14:57:48 kstaken Exp $

import sys, time, os

from XMLFragment import XMLFragment

import libxml2

def Database(config):
    
    if (config.xpathEval("/blog/db-type")[0].content == "dbxml"):
        from DBXMLDatabase import DBXMLDatabase
        return DBXMLDatabase(config)        
    elif (config.xpathEval("/blog/db-type")[0].content == "dbxml2"):
        from DBXML2Database import DBXML2Database
        return DBXML2Database(config)
    else:
        from FileDatabase import FileDatabase
        return FileDatabase(config)              
