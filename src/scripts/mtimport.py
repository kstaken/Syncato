#!/usr/local/bin/python
#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.
#
# Import data from a movabletype export file
#
# This script was derived from the mtimport script that comes with PyBloxsom

from bsddb3.db import *
from dbxml import *

import libxml2

from string import replace
import sys, re, time

entryDelimiter = re.compile( r"^--------$", re.MULTILINE )
sectionDelimiter = re.compile( r"^-----$", re.MULTILINE )

# Converts XML reserved chars to the proper entities.
def encode(data):
    data = replace(data, '&', '&amp;')
    data = replace(data, '<', '&lt;')
    data = replace(data, '>', '&gt;')
    data = replace(data, '"', '&quot;')
    data = replace(data, "'", '&apos;')
    return data

def clean(data):
    data = replace(data, '&', '&amp;')
    
    data = replace(data, '<pre>', '<pre><![CDATA[')    
    data = replace(data, '</pre>', ']]></pre>')
    
    # Fixes for the garbage HTML from outside sources
    data = replace(data, '<A HREF=', '<a href=')
    data = replace(data, '<A href=', '<a href=')    
    data = replace(data, '<MAP', '<map')    
    data = replace(data, '</A>', '</a>')
    data = replace(data, '<BR>', '<br />')
    data = replace(data, '?o=1" >', '?o=1" />')
    data = replace(data, '08-20" >', '08-20" />')
    data = replace(data, 'alt="Shop at Amazon.com">', 'alt="Shop at Amazon.com" />')
    data = replace(data, 'vspace="3">', 'vspace="3" />')
    data = replace(data, 'align=right', 'align="right"')
    data = replace(data, 'alt="">', 'alt="" />')
    data = replace(data, '<p>', '')
    data = replace(data, '</p>', '\n')
    data = replace(data, '<P>', '')
    data = replace(data, '</P>', '\n')
    data = replace(data, '</th><tr>', '</th></tr><tr>')
    data = replace(data, '<A\n', '<a\n')
    data = replace(data, '\n\n', '<p />')
    
    return data
    
def convert(fileName, database):
    input = open(inputfile).read()

    # Setup the database
    # TODO this should be using the environment
    container = XmlContainer(None, database)
    container.open(None, DB_CREATE)
   
    rejects = 0
    
    # split the file into individual posts
    entries = entryDelimiter.split(input)
    for entry in entries:
        if entry.strip():
            # Split up the sections
            sections = sectionDelimiter.split(entry)
            
            extendedbody = ""
            if (len(sections) > 2):
                extendedBody = sections[2].split(":", 1)[1]
                
            fields = sections[0].strip().split("\n")
            
            body = sections[1].split(":",1)[1]
            
            title = ""
            date = ""
            categories = []
            author = ""
            
            for field in fields:
                if (field.strip()):
                    tag, value = field.split(": ", 1)
                    if (tag == "TITLE"):
                        title = value.strip()
                    elif (tag == "DATE"):
                        date = value.strip()
                    elif (tag == "CATEGORY"):
                        categories.append(value.strip())
                    elif (tag == "AUTHOR"):
                        author = value.strip()
                    
            timeformats = ("%m/%d/%Y %I:%M:%S %p", "%m/%d/%y %I:%M:%S %p")
            for timeformat in timeformats:
                formatmatched = 0
                try:
                    timestamp = time.mktime(time.strptime(date, timeformat))
                    formatmatched = 1
                except Exception, e:
                    print str(e)
                    continue
                if formatmatched == 1:
                    break
            if formatmatched == 0:
                raise ValueError, "timeformat not matched\n" + date

            doc = libxml2.newDoc("1.0")
            root = doc.newChild(None, "item", None)
            
            titleNode = root.newChild(None, "title", None)
            titleText = doc.newDocText(encode(title))
            titleNode.addChild(titleText)
            
            try:
                body = clean(body)
                bodyDoc = libxml2.parseDoc("<description>" + body + "</description>")
                root.addChild(bodyDoc.getRootElement())
            except:
                rejects += 1
                print title
            
            for category in categories:
                root.newChild(None, "category", encode(category))
            
            pubDate = root.newChild(None, "pubDate", time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(timestamp)) + "-07:00")
            pubDate.setProp("seconds", str(timestamp))
            
            doc1 = libxml2.parseDoc(doc.serialize())

            document = XmlDocument()
            document.setContent(doc.serialize())
            container.putDocument(None, document)

    container.close()

    print "Rejected " + str(rejects)
if __name__=="__main__":
    try:
        inputfile, output_dir_root = sys.argv[1:]
    except:
        print """Usage: mt2import exportfile database
        exportfile - File containing exported Movable Type entries
        database -  path to the DB XML database to import into.
        
        Note: it is critical that no other application accesses the database
        while this is running.
        """
        sys.exit(0)

    #print encode(open("test.txt").read())
    convert(inputfile, output_dir_root)