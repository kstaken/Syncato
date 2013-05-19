<xsl:stylesheet
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
        xmlns:date="http://exslt.org/dates-and-times"        
        xmlns:dc="http://purl.org/dc/elements/1.1/"
        xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        xmlns:dbxml="http://www.sleepycat.com/2002/dbxml"
        xmlns:weblog="http://www.xmldatabases.org/weblog"        
        xmlns:dbxsl="http://www.xmldatabases.org/dbxsl"
        extension-element-prefixes="dbxsl weblog"
        xmlns="http://purl.org/rss/1.0/"
        xsl:version="1.0">
    <xsl:import href="lib.xsl"/>
    <!--xsl:variable name="config" select="document('../../config/config.xml')/blog"/-->
   
    <!-- arg will contain the name of the category -->
    <xsl:param name="arg"/>
    
    <!--xsl:variable name="dateRange" select="$config/frontpage-term * 60 * 60 * 24"/-->    
       
    <xsl:template match="/">
        <!-- Select all entries from the last n days for the provided category if given. -->
        <xsl:variable name="query">
            <xsl:choose>
                <xsl:when test="$arg">
                    /item[category='<xsl:value-of select="$arg"/>' and pubDate/@seconds > <xsl:value-of select="date:seconds() - $dateRange"/>]
                </xsl:when>
                <xsl:otherwise>
                   /item[pubDate/@seconds > <xsl:value-of select="date:seconds() - $dateRange"/>]
                </xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
        
        <xsl:variable name="queryResult" select="dbxsl:xpathQuery($config, string($query))"/>
     
        <rdf:RDF>
            <channel rdf:resource="{$config/base-url}">
                <title><xsl:value-of select="$config/title"/></title>
                <link><xsl:value-of select="$config/base-url"/></link>
                <description><xsl:value-of select="$config/description"/></description>
                <dc:language><xsl:value-of select="$config/language"/></dc:language>
                <dc:creator><xsl:value-of select="$config/webmaster"/></dc:creator>
                <dc:date><xsl:value-of select="date:date-time()"/></dc:date>
                
                <items>
                    <rdf:Seq>
                    
                    <xsl:for-each select="$queryResult">                    
                        <xsl:sort select="pubDate/@seconds" data-type="number" order="descending"/>
                        
                        <rdf:li rdf:resource="{weblog:itemlink($config/base-url, title, @id)}"/>
                                                        
                    </xsl:for-each>
                    </rdf:Seq>
                </items>
            </channel>    
            
            <xsl:apply-templates select="$queryResult">                    
                <xsl:sort select="pubDate/@seconds" data-type="number" order="descending"/>
            </xsl:apply-templates>
            
        </rdf:RDF>
    </xsl:template>
    
    <xsl:template match="item">
        <item rdf:about="{weblog:itemlink($config/base-url, title, @id)}">
            <title><xsl:value-of select="title"/></title>
            <link><xsl:value-of select="weblog:itemlink($config/base-url, title, @id)"/></link>
            <description>
            <!--xsl:copy-of select="weblog:summarize(description, 50)"/-->
            <xsl:call-template name="summarize">
                <xsl:with-param name="content" select="description"/>
                <xsl:with-param name="count" select="50"/>
            </xsl:call-template>
            
            </description>
            <dc:date><xsl:value-of select="pubDate"/></dc:date>            
        </item>
    </xsl:template>
</xsl:stylesheet>

