<xsl:stylesheet
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
        xmlns:dbxml="http://www.sleepycat.com/2002/dbxml"
        xmlns:date="http://exslt.org/dates-and-times"
        xmlns:weblog="http://www.xmldatabases.org/weblog"        
        xmlns:dbxsl="http://www.xmldatabases.org/dbxsl"
        extension-element-prefixes="dbxsl weblog"
        xsl:version="1.0">
    <xsl:import href="lib.xsl"/>
    <xsl:import href="ads.xsl"/> 
    
    <xsl:preserve-space elements="code pre"/>          
    
    <xsl:template name="main">
        <html>  
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
            <link rel="stylesheet" type="text/css" href="{$config/content-url}/{$config/css-style}"/>
        
            <link rel="alternate" type="application/rss+xml" title="RSS" href="{$config/base-url}?t={$config/preferred-rss}"/>
                       
            <xsl:call-template name="page-title"/>
        </head>
        
        <body>
            <xsl:call-template name="banner"/>
            
            <div id="content">
                <xsl:call-template name="content-head"/>
                
                <xsl:call-template name="content-body"/>
                
                <xsl:call-template name="content-foot"/>
            </div>   
            
            <xsl:call-template name="links"/>            
        </body>
        </html>
    </xsl:template>

    <xsl:template name="page-title">
        <title><xsl:value-of select="$config/title"/></title>
    </xsl:template>

    <xsl:template name="content-body">
        <xsl:apply-templates select="//item">
            <xsl:sort select="pubDate/@seconds" data-type="number" order="descending"/>
        </xsl:apply-templates>
    </xsl:template>
    
    <xsl:template name="content-head">
        <xsl:call-template name="title"/>
                
        <xsl:call-template name="google-skyscraper"/> 

    </xsl:template>
    
    <xsl:template name="content-foot">
        <div align="center" >
             <xsl:call-template name="copyright"/>             
        </div>    
    </xsl:template>
    
    <xsl:template name="title">
    </xsl:template>
    
    <xsl:template match="item">
        
        <div class="blog">
            <div class="blogbody">

            <h3 class="title"><xsl:value-of select="title" disable-output-escaping="yes"/></h3>

            <p>          
            <xsl:apply-templates select="description"/>                        
            </p>
            
            Posted by <xsl:value-of select="$config/content-owner"/><xsl:text> </xsl:text><br/>
            <!-- No point in showing the links if there's no id -->
            <xsl:if test="@id">
                <a href="{weblog:itemlink($config/base-url, title, @id)}">
                   <xsl:call-template name="date-format"><xsl:with-param name="date" select="pubDate"/></xsl:call-template>
                </a>
                |
                <a href="{weblog:itemlink($config/base-url, title, @id)}#comment">
                    Comments
                    (<xsl:choose>
                        <xsl:when test="not(comment-count)">0</xsl:when>
                        <xsl:otherwise><xsl:value-of select="comment-count"/></xsl:otherwise>
                    </xsl:choose>)
                </a>
                 <!--|
                <a href="{weblog:itemlink($config/base-url, title, @id)}#trackback">
                    Trackbacks
                    (<xsl:choose>
                        <xsl:when test="not(trackback-count)">0</xsl:when>
                        <xsl:otherwise><xsl:value-of select="trackback-count"/></xsl:otherwise>
                    </xsl:choose>)
                </a-->
            </xsl:if>
            </div>
        </div>
    
    </xsl:template>
    
    <xsl:template name="comments">
        <div class="comments-title">
            <a name="comment">Comments</a>
        </div>
            
        <xsl:variable name="query">/comment[@postID = <xsl:value-of select="@id"/>]</xsl:variable>
        <xsl:apply-templates select="dbxsl:xpathQuery($config, string($query))">
            <xsl:sort data-type="number" order="ascending" select="pubDate/@seconds"/>
        </xsl:apply-templates>
        
        <div class="comments-title">
            <a name="trackback">Trackbacks</a>           
        </div>
        Trackback URL for this post: 
        <xsl:value-of select="$config/system-url"/>/Trackback/<xsl:value-of select="@id"/>
        
        <xsl:variable name="tb-query">/trackback[@postID = <xsl:value-of select="@id"/>]</xsl:variable>
        <xsl:apply-templates select="dbxsl:xpathQuery($config, string($tb-query))">
            <xsl:sort data-type="number" order="ascending" select="pubDate/@seconds"/>
        </xsl:apply-templates>
        
        <div class="comments-title">
        Post a comment
        </div>
        
        <div class="comments-body">
            <form method="post" action="{$config/system-url}/Comment">
            <input type="hidden" name="/comment/@postID" value="{@id}" />
            
            Name:<br />
            <input name="/comment/author" size="50" /><br /><br />
                       
            URL:<br />
            <input name="/comment/url" size="50" />
            <input type="hidden" name="#blacklist#/comment/url" value="{$config/blacklist-message}"/>
            <br /><br />
            
            Comments:<br />
            <textarea name="/comment/body#markup" rows="15" cols="70"><xsl:text> </xsl:text></textarea><br /><br />
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
            
            <!-- If the authors name wasn't provided then they should be listed
                 as anonymous -->
            <xsl:variable name="author">
                <xsl:choose>
                    <xsl:when test="author">
                        <xsl:value-of select="author"/>
                    </xsl:when>
                    <xsl:otherwise>
                        Anonymous
                    </xsl:otherwise>
                </xsl:choose>
            
            </xsl:variable>
                        
            <span class="comments-post">
                Posted by: 
                
                <!-- We only want to link if a url was actually provided -->
                <xsl:choose>
                    <xsl:when test="url">
                        <a target="_blank" href="{url}">
                            <xsl:value-of select="$author"/>
                        </a>    
                    </xsl:when>
                    <xsl:otherwise>
                        <b><xsl:value-of select="$author"/></b>                    
                    </xsl:otherwise>
                </xsl:choose>            
                on 
                <xsl:call-template name="date-format"><xsl:with-param name="date" select="pubDate"/></xsl:call-template>
            </span>
        </div>
    </xsl:template>
    
    <xsl:template match="trackback">
        <div class="comments-body">
            <b><xsl:value-of select="title"/></b>
            <p><xsl:apply-templates select="excerpt" disable-output-escaping="yes"/></p>

            <p/>            
            <span class="comments-post">
                Trackback from: 
                
                <!-- We only want to link if a url was actually provided -->
                <xsl:choose>
                    <xsl:when test="blog_name">
                        <a target="_blank" href="{url}">
                            <xsl:value-of select="blog_name"/>
                        </a>    
                    </xsl:when>
                    <xsl:otherwise>
                        <a target="_blank" href="{url}">
                            <xsl:value-of select="url"/>
                        </a>                     
                    </xsl:otherwise>
                </xsl:choose>            
                on 
                <xsl:call-template name="date-format"><xsl:with-param name="date" select="pubDate"/></xsl:call-template>
            </span>
        </div>
    </xsl:template>
    
    <xsl:template name="banner">
        <div id="banner">
            <h1>
            <a href="{$config/base-url}/">
                <xsl:value-of select="$config/title"/>
            </a>
            </h1>
            <span class="description"><xsl:value-of select="$config/description"/></span>
        </div>
    </xsl:template>
    
    <xsl:template name="links">
        <div id="links">
            <xsl:call-template name="syndicate"/>
            
            <xsl:call-template name="category-list"/>
     
            <xsl:call-template name="recent-entries"/>
            
            <!--xsl:call-template name="recent-comments"/-->
            
            <xsl:call-template name="powered-by"/>                       
        </div>

    </xsl:template>
    
</xsl:stylesheet>

