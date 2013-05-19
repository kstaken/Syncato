#!/usr/local/bin/python
#
# See the file LICENSE for redistribution information.
#
# Copyright (c) 2003 Kimbro Staken. All rights reserved.
#
# $Id: Weblog.py,v 1.13 2004/04/15 09:29:05 kstaken Exp $
import Framework

from urllib import unquote
from Exceptions import *
            
class Router:
    
    def _parseRequest(self, method, pathInfo, request, response):
        # Defaults if no specific settings are passed in.
        site = "default"
        component = "weblog"
        controller = "index"
        action = method
        view = ""
        recordID = -1

        # extract the site instance from the path Info
        pathComponents = pathInfo.split("/") 
        if (len(pathComponents) > 1):
            site = pathComponents[1]
            if (len(pathComponents) > 2):
                if (pathComponents[2] != ""):
                    (component, view, recordID) = self._checkComponent(pathComponents[2], "weblog")

            if (len(pathComponents) > 3):
                if (pathComponents[3] != ""):
                    (controller, view, recordID) = self._checkComponent(pathComponents[3], "index")

            if (len(pathComponents) > 4):
                if (pathComponents[4] != ""):
                    (action, view, recordID) = self._checkComponent(pathComponents[4], "index")

        # If there's a view specified in the parameters it overrides what we already determined 
        view = request.field('t', view)
        
        # Add the query to the request 
        query = request.field('q', "")
        
        # optional argument to the view
        arg = request.field('a', "")
        
        context = {
            'site': site,
            'component': component,
            'controller': controller,
            'action': action,
            'view': view,
            'recordID': recordID,
            'query': query,
            'arg': arg,
            'request': request,
            'response': response
        }
        
        return context

    def _checkComponent(self, component, default):
        # Check to see if there's a view name after the dot
        result = component
        view = unquote(result).split(".")
        if (len(view) > 1):
            result = view[0]
            view = view[-1]

        else:
            view = ""

        # now see if component contains a numeric record ID
        recordID = -1
        try:                
            names = result.split("_")
            if (len(names) > 1):
                recordID = int(names[0])
            else:
                recordID = int(result)  
            
            result = default                  
        except (ValueError, IndexError):            
            pass
            
        return (result, view, recordID) 
        
    def _verifyRoute(self, context):
        method = None
        
        # get the site
        site = Framework.Framework().getSite(context['site'])
        
        print "looking for component " + context['component']
        # check for the component under the site
        component = site.getComponent(context['component'])
        
        # If it's not found, check for the component under the application
        if (component == None):
            component = Framework.Framework().getComponent(context['component'])
        
        if (component == None):
            # TODO raise some kind of error
            pass
        
        # Verify the requested controller exists in the component
        controller = component.getController(context['controller'])
        
        # verify that the action exists in the controller
        if (controller):
            controller.db = site.getDatabase()
            controller.site = site
            
            method = getattr(controller, context['action'])
        
        return (site, method)
        
    def processRequest(self, method, pathInfo, request, response):
        # Get the route
        context = self._parseRequest(method, pathInfo, request, response)
        
        # verify the route and get the executable object to invoke
        (site, executable) = self._verifyRoute(context)
        
        # Execute the requested action
        print "Executing action " + context['action']

        result = None
        #try:
        result = executable(context)        
        #except NotFoundError:
        #    response.setStatus(404, 'Not Found')
        #except:
        #    response.setStatus(500, 'Server Error')
            
        if (result):
            # render the view if there is one.
            if (context['view'] != ""):
                if (site.getDatabase().locateStylesheet(context['view']) != None):
                    result = site.getDatabase().runTransform(result, context['view'], context['arg'])

            print result
            # Determine the content-type for the result
            if (result.startswith("<?xml")):                             
                 contentType = "text/xml"         
            elif (result.startswith("<html")):
                 contentType = "text/html"
            else:
                 contentType = "text/plain"
            #print result
     
            response.setStatus(200, 'OK')
            response.setHeader('Content-type', contentType)
            response.setHeader('Content-length', str(len(result)))
            response.write(result)
