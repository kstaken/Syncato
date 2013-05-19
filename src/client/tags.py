#!/usr/bin/python
#
# Asks the user for an html link and then replaces the text with the proper HTML
#
# -- TextExtras User Script Info --
#
# -- TextExtras User Script Info --
# %%%{TENewScript}%%%
# %%%{TEName=New Blog Entry}%%%
# %%%{TEInput=AllText}%%%
# %%%{TEOutput=ReplaceAllText}%%%
# %%%{TEKeyEquivalent=^@n}%%%
# %%%{TEArgument=n}%%%
#
# %%%{TENewScript}%%%
# %%%{TEName=Link Text}%%%
# %%%{TEInput=Selection}%%%
# %%%{TEOutput=ReplaceSelection}%%%
# %%%{TEKeyEquivalent=^@l}%%%
# %%%{TEArgument=l}%%%
#
# %%%{TENewScript}%%%
# %%%{TEName=RZ Link Text}%%%
# %%%{TEInput=Selection}%%%
# %%%{TEOutput=ReplaceSelection}%%%
# %%%{TEKeyEquivalent=^@y}%%%
# %%%{TEArgument=rl}%%%
#
# %%%{TENewScript}%%%
# %%%{TEName=Paragraph}%%%
# %%%{TEInput=Selection}%%%
# %%%{TEOutput=ReplaceSelection}%%%
# %%%{TEKeyEquivalent=^@p}%%%
# %%%{TEArgument=p}%%%
#
# %%%{TENewScript}%%%
# %%%{TEName=Amazon Product}%%%
# %%%{TEInput=Selection}%%%
# %%%{TEOutput=ReplaceSelection}%%%
# %%%{TEKeyEquivalent=^@a}%%%
# %%%{TEArgument=a}%%%
#
# %%%{TENewScript}%%%
# %%%{TEName=Pre Tag}%%%
# %%%{TEInput=Selection}%%%
# %%%{TEOutput=ReplaceSelection}%%%
# %%%{TEKeyEquivalent=^@c}%%%
# %%%{TEArgument=c}%%%
#
# %%%{TENewScript}%%%
# %%%{TEName=RZ Pre Tag}%%%
# %%%{TEInput=Selection}%%%
# %%%{TEOutput=ReplaceSelection}%%%
# %%%{TEKeyEquivalent=^@r}%%%
# %%%{TEArgument=r}%%%
#
# %%%{TENewScript}%%%
# %%%{TEName=}%%%
# %%%{TEInput=Selection}%%%
# %%%{TEOutput=ReplaceSelection}%%%
# %%%{TEKeyEquivalent=}%%%

import sys, os

INPUT = sys.stdin.read()

arg = sys.argv[1]
if (arg == "l"):
    url = os.popen('%%%{TEUtilityScriptsPath}%%%/AskUserForStringDialog "http://"').read().strip()
    
    if (url != ""):            
        sys.stdout.write('<a href="' + url + '">' + INPUT + '%%%{TESelection}%%%</a>')
if (arg == "rl"):
    url = os.popen('%%%{TEUtilityScriptsPath}%%%/AskUserForStringDialog "http://"').read().strip()
    
    if (url != ""):            
        sys.stdout.write('[' + INPUT + '%%%{TESelection}%%%|' + url + ']')
elif (arg == "p"):    
    sys.stdout.write("<p>\n" + INPUT + "%%%{TESelection}%%%\n</p>")
elif (arg == "a"):    
    sys.stdout.write("<asin>" + INPUT + "%%%{TESelection}%%%</asin>")
elif (arg == "c"):    
    sys.stdout.write("<pre><![CDATA[\n" + INPUT + "%%%{TESelection}%%%\n]]></pre>")
elif (arg == "r"):    
    sys.stdout.write("r'''<pre><![CDATA[\n" + INPUT + "%%%{TESelection}%%%\n]]></pre>'''")
elif (arg == "n"):    
    print "id: action:new format:rz"
    print ""
    print "title: %%%{TESelection}%%%"
    print "categories:"
    print ""
    print INPUT

