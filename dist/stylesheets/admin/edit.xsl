<xsl:stylesheet
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
        xmlns:dbxml="http://www.sleepycat.com/2002/dbxml"
        xmlns:date="http://exslt.org/dates-and-times"
        xmlns:weblog="http://www.xmldatabases.org/weblog"        
        xmlns:dbxsl="http://www.xmldatabases.org/dbxsl"
        extension-element-prefixes="dbxsl weblog"
        xsl:version="1.0">
    <xsl:import href="../../../stylesheets/layout.xsl"/> 
    
    <xsl:template match="/">
        <xsl:call-template name="main"/>
    </xsl:template>
 
     <xsl:template name="main">
        <html>  
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
            <link rel="stylesheet" type="text/css" href="{$config/content-url}/{$config/css-style}"/>
 
            <title>Syncato Admin</title>
        </head>
        
        <body bgcolor="#ffffff">
            <xsl:call-template name="banner"/>
            
            <xsl:call-template name="links"/>
            
            <xsl:call-template name="body"/>          
        </body>
        </html>
    </xsl:template>
    
    <xsl:template name="error">
        <xsl:if test="//error-text">
            <div class="comments-title">
                Your post contains some errors that must be corrected.
            </div>
            
            <div class="error">
                <xsl:apply-templates select="//error-text"/>
            </div>
        </xsl:if> 
    </xsl:template>
    
    <xsl:template match="error-text">
        <xsl:value-of select="."/>
    </xsl:template>
    
    <xsl:template name="links">
        <div id="links"> 
            <div class="sidetitle">
            Tools
            </div>
            
            <div class="side">
                <a href="{$config/admin-url}">New Post</a><br/>
                <a href="{$config/base-url}?t=page/editor">New Page</a><br/>
                <a href="{$config/base-url}?t=category/editor">New Category</a>
            </div>   
            
            <div class="sidetitle">
            Collections
            </div>
            
            <div class="side">
                <a href="{$config/admin-url}/collection/item">Posts</a><br/>
                <a href="{$config/admin-url}/collection/page">Pages</a><br/>
                <a href="{$config/admin-url}/collection/comment">Comments</a><br/>
                <a href="{$config/admin-url}/collection/trackback">Trackbacks</a><br/>
                <a href="{$config/admin-url}/collection/category">Categories</a><br/>
                <a href="{$config/admin-url}/collection/blacklist">Spam Blacklist</a>                
            </div>      
            
            <div class="sidetitle">
            Recent Posts
            </div>
            
            <div class="side">
            <xsl:call-template name="recent-entries"/>
            </div>                                              
        </div>
    </xsl:template>
    
    <!-- Shows the list of recently added item entries -->
    <xsl:template name="recent-entries">        
        <xsl:for-each select="dbxsl:xpathQuery($config, string($itemQuery))">
            <xsl:sort select="pubDate/@seconds" data-type="number" order="descending"/>
            <a href="{$config/base-url}/{@id}?t=item/editor">
                 <xsl:value-of select="title"/><br/>
            </a>                        
        </xsl:for-each>
        <span/>
    </xsl:template>
    
    <xsl:template name="banner">
        <div id="banner">
            <h1>
            <a>
                <xsl:attribute name="href"><xsl:value-of select="$config/base-url"/></xsl:attribute>
                Syncato Admin
            </a>
            </h1>
            <span class="description">Tools to help out</span>
        </div>
    </xsl:template>    
</xsl:stylesheet>

