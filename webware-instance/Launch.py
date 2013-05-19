#!/usr/bin/env python

import os, sys

# These must be set for the location of your installation
webwarePath = '../Webware-0.9'
appWorkPath = '/Users/kstaken/Workspace/SyncatoSites/www.xmldatabases.org/syncato-0.8/webware'
appWorkPath = '.'

sys.path.append('../src/lib')
#sys.path.append('../dist/client')


def main(args):
	global webwarePath, appWorkPath
	newArgs = []
	for arg in args:
		if arg.startswith('--webware-path='):
			webwarePath = arg[15:]
		elif arg.startswith('--working-path='):
			appWorkPath = arg[15:]
		else:
			newArgs.append(arg)
	args = newArgs
	# ensure Webware is on sys.path
	sys.path.insert(0, webwarePath)

	# import the master launcher
	import WebKit.Launch

	if len(args) < 2:
		WebKit.Launch.usage()

	# Go!
	WebKit.Launch.launchWebKit(args[1], appWorkPath, args[2:])


if __name__=='__main__':
	main(sys.argv)
