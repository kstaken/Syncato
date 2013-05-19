<xsl:stylesheet
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
        xmlns:dbxml="http://www.sleepycat.com/2002/dbxml"
        xmlns:date="http://exslt.org/dates-and-times"
        xmlns:weblog="http://www.xmldatabases.org/weblog"        
        xmlns:dbxsl="http://www.xmldatabases.org/dbxsl"
        extension-element-prefixes="dbxsl weblog"
        xsl:version="1.0">
    <xsl:output method="xml"  omit-xml-declaration="yes"/>
    <xsl:preserve-space elements="code pre script"/>
    
    <xsl:param name="site_id"/>

    <!-- Read in the configuration so that we can set properties in the stylesheet -->
    <xsl:variable name="config" select="weblog:getConfig($site_id)"/>
    
    <!-- The syncato version -->
    <xsl:variable name="version">0.8</xsl:variable>
    
    <!-- Query is /item[pubDate/@seconds > now() - 604800]
        This selects all the posts made in the last seven days. -->
    <xsl:variable name="dateRange" select="$config/frontpage-term * 60 * 60 * 24"/>    
    <xsl:variable name="itemQuery">/item[pubDate/@seconds > <xsl:value-of select="date:seconds() - $dateRange"/>]</xsl:variable>

    <!-- Selects the comments posted in the last seven days -->
    <xsl:variable name="commentQuery">/comment[pubDate/@seconds > <xsl:value-of select="date:seconds() - $dateRange"/>]</xsl:variable>
        
    <xsl:template match="description">
        <xsl:apply-templates disable-output-escaping="yes"/>
    </xsl:template>
       
    <!-- Runs an XPath query against the local database -->
    <xsl:template match="xpath-query">
        <xsl:apply-templates select="dbxsl:xpathQuery($config, string(.))"/>
    </xsl:template>
    
    <!-- Runs an XPath query against a remote Syncato instance -->
    <xsl:template match="remote-xpath-query">
        <xsl:apply-templates select="document(weblog:urlencode(string(.)))/results"/>
    </xsl:template>
    
    <!-- Includes the content of a remote XML file -->
    <xsl:template match="remote-content">
        <xsl:apply-templates select="document(weblog:urlencode(string(.)))"/>
    </xsl:template>
    
    <xsl:template match="content-box">
        <div class="sidetitle">
            <xsl:value-of select="title"/>
        </div>
        
        <div class="side">
            <xsl:apply-templates select="body/node()"/>
        </div>        
    </xsl:template>

    <!-- Displays a list of item headlines using the provided query -->
    <xsl:template match="title-list">    
        <xsl:for-each select="dbxsl:xpathQuery($config, string(.))/title">
            <xsl:sort select="../pubDate/@seconds" data-type="number" order="descending"/>

            <p><a href="{weblog:itemlink($config/base-url, ../title, ../@id)}">
               <xsl:value-of select="." disable-output-escaping="yes"/>
            </a></p>
        </xsl:for-each>        
    </xsl:template>
            
    <!-- Displays a list of item headlines bases on the provided query -->
    <xsl:template match="headline-list">
        <!-- Use the provided query, but restrict it to $dateRange days -->
        <xsl:variable name="query">
            /item[<xsl:value-of select="."/> and pubDate/@seconds > <xsl:value-of select="date:seconds() - $dateRange"/>]
        </xsl:variable>
        
        <xsl:apply-templates select="dbxsl:xpathQuery($config, string($query))/title" mode="headline-list">
            <xsl:sort select="../pubDate/@seconds" data-type="number" order="descending"/>
        </xsl:apply-templates>        
    </xsl:template>
        
    <xsl:template match="title" mode="headline-list">
        <a href="{weblog:itemlink($config/base-url, ., ../@id)}">
            <xsl:value-of select="." disable-output-escaping="yes"/><br/>
        </a>
    </xsl:template>
    
    <!-- Subtopics are used on FAQ items. We don't want them to display normally. -->
    <xsl:template match="subtopic">
    </xsl:template>
    
    <!-- Shows the list of categories that are defined in the system. -->
    <xsl:template name="category-list">
        <div id="category-list">
            <div class="sidetitle">
            Categories
            </div>
            
            <div class="side">
                <xsl:for-each select="dbxsl:xpathQuery($config, '/category-def')">            
                    <a href="{$config/base-url}?t=category&amp;a={title}">
                        <xsl:value-of select="title"/>
                    </a><xsl:text> </xsl:text>         
                    <a class="rss-text" href="{$config/base-url}?t=rss20&amp;a={title}">
                        (RSS)
                    </a><br/>
                </xsl:for-each>
                
                <span/>
            </div>
        </div>
    </xsl:template>

    <!-- Shows the list of recently added item entries -->
    <xsl:template name="recent-entries">        
        <div id="recent-entries">
            <div class="sidetitle">
                Recent Entries
            </div>
            
            <div class="side">
                <xsl:for-each select="dbxsl:xpathQuery($config, string($itemQuery))">
                    <xsl:sort select="pubDate/@seconds" data-type="number" order="descending"/>
                    <a href="{weblog:itemlink($config/base-url, title, @id)}">
                        <xsl:value-of select="title"/><br/>
                    </a>                        
                </xsl:for-each>
                <span/>
            </div>  
        </div>
    </xsl:template>

    <!-- Shows the list of recently added comments -->
    <xsl:template name="recent-comments">  
        <div id="recent-comments">
            <div class="sidetitle">
            Recent Comments
            </div>
            <div class="side">
                <xsl:for-each select="dbxsl:xpathQuery($config, string($commentQuery))">
                    <xsl:sort select="pubDate/@seconds" data-type="number" order="descending"/>
                    <a href="{$config/base-url}/{@postID}?t=item#comment">
                        <xsl:value-of select="weblog:summarize(body, 5)"/>
                    </a> by 
                    <xsl:choose>
                        <xsl:when test="author">
                            <xsl:value-of select="author"/>
                        </xsl:when>
                        <xsl:otherwise>
                            Anonymous
                        </xsl:otherwise>
                    </xsl:choose>
                    <br/>                        
                </xsl:for-each>
                
                <span/>
            </div>
        </div>
        
    </xsl:template>
    
    <xsl:template name="syndicate">
        <div id="syndicate">
            <div class="sidetitle">
                Syndicate
            </div>
            
            <div class="syndicate">
                <a href="{$config/base-url}?t={$config/preferred-rss}">
                Syndicate this site (XML - RSS)</a>
            </div>
        </div>
    </xsl:template>

    <xsl:template name="copyright">
        <div align="center" >
            Copyright <xsl:value-of select="$config/copyright"/><xsl:text> </xsl:text><xsl:value-of select="$config/content-owner"/>
        </div>  
    </xsl:template>
            
    <xsl:template name="summarize">
        <xsl:param name="content"/>
        <xsl:param name="count"/>
        
        <!-- Apply templates to expand all markup -->
        <xsl:variable name="body">
            <xsl:apply-templates select="$content"/>
        </xsl:variable>
        
        <!-- Now strip away the markup -->
        <xsl:variable name="bodyNoTags">
            <xsl:value-of select="$body"/>
        </xsl:variable>
            
        <xsl:value-of select="weblog:summarize($bodyNoTags, $count)"/>    
    </xsl:template>
    
    <xsl:template name="date-format">
        <xsl:param name="date"/>
        
        <!-- Format the date. This is way ugly -->
        <xsl:value-of select="date:day-name($date)"/><xsl:text> </xsl:text>
        <xsl:value-of select="date:month-abbreviation($date)"/><xsl:text> </xsl:text>
        <xsl:value-of select="date:day-in-month($date)"/>, 
        <xsl:value-of select="date:year($date)"/> at 
        
        <xsl:choose>
            <xsl:when test="date:hour-in-day($date) > 11 and date:hour-in-day($date) &lt; 24">
                <xsl:value-of select="date:hour-in-day($date) - 12"/>:<xsl:value-of select="format-number(date:minute-in-hour($date), '00')"/> PM
            </xsl:when>
            <xsl:when test="date:hour-in-day($date) = 11">
                12:<xsl:value-of select="format-number(date:minute-in-hour($date), '00')"/> PM
            </xsl:when>
            <xsl:when test="date:hour-in-day($date) = 0">
                12:<xsl:value-of select="format-number(date:minute-in-hour($date), '00')"/> AM
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="date:hour-in-day($date)"/>:<xsl:value-of select="format-number(date:minute-in-hour($date), '00')"/> AM
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
        
    <xsl:template match="powered-by" name="powered-by">
        <div class="sidetitle">
        Powered By
        </div>
        
        <div class="side">
            <a href="http://www.syncato.org/">Syncato <xsl:value-of select="$version"/></a>
        </div> 
    </xsl:template>
            
    <!-- identity transform to copy through everything by default -->   
    <xsl:template match="node()|@*">
        <xsl:copy><xsl:apply-templates select="@*"/><xsl:apply-templates/></xsl:copy>
    </xsl:template>
 
</xsl:stylesheet>

