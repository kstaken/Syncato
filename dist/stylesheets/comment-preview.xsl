<xsl:stylesheet
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
        xmlns:dbxml="http://www.sleepycat.com/2002/dbxml"
        xmlns:date="http://exslt.org/dates-and-times"
        xmlns:weblog="http://www.xmldatabases.org/weblog"        
        xmlns:dbxsl="http://www.xmldatabases.org/dbxsl"
        extension-element-prefixes="dbxsl weblog"
        xsl:version="1.0">
    <xsl:import href="layout.xsl"/> 
    
    <xsl:template match="/">
        <xsl:call-template name="main"/>
    </xsl:template>
 
    <xsl:template name="main">
        <html>  
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
            <link rel="stylesheet" type="text/css" href="{$config/content-url}/{$config/css-style}"/>

            <title><xsl:value-of select="$config/title"/></title>
        </head>
        
        <body bgcolor="#ffffff">  
            <xsl:call-template name="banner"/>
            
            <xsl:call-template name="links"/>
                                            
            <div id="content">
                
                <xsl:call-template name="comments"/>                                
                
                <div align="center" >
                     Copyright <xsl:value-of select="$config/copyright"/><xsl:text> </xsl:text><xsl:value-of select="$config/content-owner"/>
                </div>    
            </div>            
            
        </body>
        </html>
    </xsl:template>
    
    <xsl:template name="comments">
        <xsl:if test="comment/error-text">
            <div class="comments-title">
                Your post contains some errors that must be corrected.
            </div>
                
            <div class="error">
                <xsl:apply-templates select="comment/error-text/node()"/>
            </div>
        </xsl:if>
        
        <div class="comments-title">
            Comments
        </div>
            
        <xsl:apply-templates select="/comment">
            <xsl:sort select="pubDate/@seconds" data-type="number" order="descending"/>
        </xsl:apply-templates>
        
        <div class="comments-title">
        Post a comment
        </div>
        
        <div class="comments-body">
            <form method="post" action="{$config/system-url}/Comment">
            <input type="hidden" name="/comment/@postID" value="{comment/@postID}" />
            
            Name:<br />
            <input name="/comment/author" value="{comment/author}" size="50"/><br /><br />
                       
            URL:<br />
            <input name="/comment/url" value="{comment/url}" size="50"/>
            <input type="hidden" name="#blacklist#/comment/url" value="{$config/blacklist-message}"/>
            <br /><br />
            
            Comments:<br />
            <textarea name="/comment/body#markup" rows="15" cols="80"><xsl:value-of select="weblog:serialize(comment/body/node())" disable-output-escaping="yes"/></textarea><br /><br />
            <input type="hidden" name="#required#/comment/body" value="You must type some comment text."/>
            <input type="hidden" name="#blacklist#/comment/body" value="{$config/blacklist-message}"/>
            
            <input type="submit" name="preview" value="Preview" />
            <input type="submit" name="post" value="Post" /><br /><br />
            
            </form>             
        </div>                        
    </xsl:template>
    
    <xsl:template match="comment">
        <div class="comments-body">
            <p><xsl:apply-templates select="body" disable-output-escaping="yes"/></p>

            <p/>
            
            <span class="comments-post">Posted by: <a target="_blank" href="{url}"><xsl:value-of select="author"/></a> 
            </span>
        </div>
    </xsl:template>    
</xsl:stylesheet>

