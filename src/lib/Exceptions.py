#!/usr/local/bin/python
#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.
#  
# $Id: DBXMLDatabase.py,v 1.7 2004/02/18 08:10:40 kstaken Exp $

class NotFoundError (Exception):
    """
    Exception that is thrown when a document can't be located in the database.
    """
    pass
 
class ParseError (Exception):
    """
    Exception that is thrown when a document can't be parsed.
    """
    pass

class PermissionDenied (Exception):
    """
    Exception that is thrown when a user is denied access to a resource.
    """
    pass
    
class PermissionGranted (Exception):
    """
    Exception that is thrown when user is granted access to a resource.
    """
    pass