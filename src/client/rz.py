#!/usr/bin/python
#
# Asks the user for an html link and then replaces the text with the proper HTML
#
# -- TextExtras User Script Info --
# %%%{TEName=Process with rhizml}%%%
# %%%{TEInput=Selection}%%%
# %%%{TEOutput=ReplaceSelection}%%%
# %%%{TEKeyEquivalent=^@r}%%%


import sys, os
import StringIO

sys.path.append('/Users/kstaken/Workspace/Book/Blog/dist/scripts/lib')
sys.path.append("/Users/kstaken/Workspace/Book/Blog/client/rhizml")

import rhizml

INPUT = sys.stdin.read()

print rhizml.rhizml2xml(StringIO.StringIO(INPUT), prettyprint=True)