Syncato is a weblog system that makes extensive use of XML and XPath. All posts
are stored in the database as XML and can be queried to any level. This combined
with XSL-T enables a powerful system for the reuse of weblog content and 
should hopefully open some new doors on the creative use of weblog content. 

This is a very preliminary guide to getting it up and running. 
Check http://www.xmldatabases.org/ for updates as I get some feedback. 

Installation
================================================================================

Syncato can be installed in two configurations. One that uses a file based 
database and one that uses a Berkeley DB XML database. Since it is much easier 
to get the system up and running with the file based database it is recommended
to start with that and then later move to DB XML as the site grows. Since all 
the data in the system is XML this transition is pretty painless.

At the present time Syncato has been tested on Linux and Mac OS X, but should
run on any UNIX system.

Software requirements
--------------------------------------------------------------------------------

For a basic Syncato install using a file based database you must install the 
following packages. See the documentation included in each package for 
instructions on how to install it. 

Python - The system has been tested with Python 2.3 though 2.2 will probably
    work too. If you don't have Python already start by installing it. Then 
    install the rest.

libxml with python extensions - http://xmlsoft.org/downloads.html
    Make sure the python extensions get built. Tested with 2.5.7

libxslt with python extensions - http://xmlsoft.org/downloads.html
    Make sure the python extensions and exslt get built. Tested with 1.0.32

Webware 0.8.1 - http://webware.sourceforge.net/
    Get this working through the web server before going on.

You also need a webserver, Apache is what's been tested, but others may work as
well. 

Some platforms might need libconv, linux shouldn't. 

libiconv - http://www.gnu.org/software/libiconv/#downloading

Adding Berkeley DB XML
--------------------------------------------------------------------------------

If you also want to install Berkeley DB XML you will need the following 
additional packages. If you are just using files you can skip to the webware
section.

Berkeley DB XML 1.1.0 with Python support - http://www.sleepycat.com/products/xml.shtml
    DB XML will also require the following packages
        Berkeley DB 4.1.25 - http://www.sleepycat.com/
        
        Xerces C 2.3 - http://xml.apache.org/dist/xerces-c/stable/
        
        Pathan 1.2 release 2 - http://software.decisionsoft.com/pathanDownload.html
            
        bsddb3 - http://pybsddb.sourceforge.net/
            Python 2.3 includes this module, but they changes the name. I just 
            installed it again under the old name.
            

Berkeley DB XML requires the LD_LIBRARY_PATH be set to the location of the 
DB XML and Berkeley DB libraries.

LD_LIBRARY_PATH=/usr/local/BerkeleyDB.4.1/lib/:/usr/local/lib:/usr/local/BerkeleyDBXML.1.1/lib

on Mac OS X this is

DYLD_LIBRARY_PATH=/usr/local/BerkeleyDB.4.1/lib/:/usr/local/lib:/usr/local/BerkeleyDBXML.1.1/lib

Make sure these settings are available to the webware instance.

Installing Webware
--------------------------------------------------------------------------------
You should install Webware based on the instructions that come in the Webware
distribution. Once you have a basic Webware instance running you should then 
shut it down and setup the Syncato instance.

The distribution includes a Webware configuration which will work if you set the 
location where Webware is installed. This is set in webware/Launch.py. You 
should set 'webwarePath' to the location where Webware is installed and 
'appWorkPath' to the directory where your copy of Launch.py is installed.

Once you do that you can start that partiular Webware instance by running the 
AppServer script in the same directory.

Configuring Apache
--------------------------------------------------------------------------------

For security, setup Webware with restrictions on POST PUT and DELETE for the 
blog URL to the site and on all methods for the admin URL. You want 
the base URL open so that you can have open comments, but the /WK/blog URL 
should be protected. Note: you don't have to use the /WK/blog URL, you can use 
something else, but it does have to have two levels.

<Location /WK>
    WKServer localhost 8086
    SetHandler webkit-handler
</Location>
<Location /WK/blog>
    AuthName "blog"
    AuthType Basic
    AuthUserFile /path/to/users

    <Limit POST PUT DELETE>
        require valid-user
    </Limit> 
</Location>
<Location /WK/admin>
    AuthName "blog"
    AuthType Basic
    AuthUserFile /path/to/users

    require valid-user 
</Location>

You'll need to use htpasswd to create the users file and user account to use 
for authentication.

Syncato also includes a style sheet, syncato.css that should be copied somewhere
accessible via HTTP. Then set /blog/content-url in config/config.xml to the 
base of the URL where syncato.css can be reached.

Configuring Syncato
--------------------------------------------------------------------------------

Syncato stores all its configuration data in config/config.xml so that file is
probably worth taking a look at. Note, webware needs to be able to write to the 
directory identified by /blog/db-location, /blog/cache-location and maybe a few 
other things.

The default style is just the one from my site. I'm sure you'll want to change 
it.

Note: the default style shows ads and config.xml contains the settings to setup
the accounts. If you want to help out the development of this software you can
keep the ads on your site without changing the account info and the revenue 
will go to me. It's a small amount, but helps.

If all goes well you can start webware by running AppServer and then access the
site at http://localhost/WK/blog.

There are a number of ways to add content to the system.

1. A rudimentary web interface http://localhost/WK/admin/Admin.
2. Using a client that supports the Blogger or MetaWeblog APIs. Configure the
    client to access http://localhost/WK/Metaweblog
3. Using the python scripts inluded with the software under the client 
    directory.
4. Using any language that can make HTTP, GET, POST, PUT and DELETE requests.

You can also edit though not create content by using an editor that supports 
storing data via HTTP PUT.    

