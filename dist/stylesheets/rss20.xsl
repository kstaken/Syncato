<xsl:stylesheet
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform"        
        xmlns:date="http://exslt.org/dates-and-times"        
        xmlns:dc="http://purl.org/dc/elements/1.1/"
        xmlns:dbxml="http://www.sleepycat.com/2002/dbxml"
        xmlns:weblog="http://www.xmldatabases.org/weblog"        
        xmlns:dbxsl="http://www.xmldatabases.org/dbxsl"
        extension-element-prefixes="dbxsl weblog"
        xsl:version="1.0">
    <xsl:param name="site_id"/>

    <!-- Read in the configuration so that we can set properties in the stylesheet -->
    <xsl:variable name="config" select="weblog:getConfig($site_id)"/>
    
    <!-- arg will contain the name of the category -->
    <xsl:param name="arg"/>
    
    <xsl:variable name="dateRange" select="$config/frontpage-term * 60 * 60 * 24"/>    
       
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
     
        <rss version="2.0">
            <channel>
                <title><xsl:value-of select="$config/title"/></title>
                <link><xsl:value-of select="$config/base-url"/></link>
                <description><xsl:value-of select="$config/description"/></description>
                <language><xsl:value-of select="$config/language"/></language>
                <webMaster><xsl:value-of select="$config/webmaster"/></webMaster>
                <dc:date><xsl:value-of select="date:date-time()"/></dc:date>
                <xsl:apply-templates select="$queryResult">
                    <xsl:sort select="pubDate/@seconds" data-type="number" order="descending"/>
                </xsl:apply-templates>
            </channel>
        </rss>
    </xsl:template>
    
    <xsl:template match="item">
        <item>
            <title><xsl:value-of select="title"/></title>
            <link><xsl:value-of select="weblog:itemlink($config/base-url, title, @id)"/></link>
            <description><xsl:copy-of select="weblog:summarize(description, 50)"/></description>
            <dc:date><xsl:value-of select="pubDate"/></dc:date>
            <guid><xsl:value-of select="weblog:itemlink($config/base-url, title, @id)"/></guid>
        </item>
    </xsl:template>
</xsl:stylesheet>

