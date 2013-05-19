#!/usr/bin/python
#
# Asks the user for an html link and then replaces the text with the proper HTML
#
# -- TextExtras User Script Info --
# %%%{TEName=Process with Textile}%%%
# %%%{TEInput=Selection}%%%
# %%%{TEOutput=ReplaceSelection}%%%
# %%%{TEKeyEquivalent=^@t}%%%


import sys, os

sys.path.append('/Users/kstaken/Workspace/Book/Blog/dist/scripts/lib')

import textile

INPUT = sys.stdin.read()

print textile.textile(INPUT)