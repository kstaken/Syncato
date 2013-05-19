<xsl:stylesheet
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
        xmlns:dbxml="http://www.sleepycat.com/2002/dbxml"
        xmlns:date="http://exslt.org/dates-and-times"
        xmlns:weblog="http://www.xmldatabases.org/weblog"        
        xmlns:dbxsl="http://www.xmldatabases.org/dbxsl"
        extension-element-prefixes="dbxsl weblog"
        xsl:version="1.0">
    <xsl:import href="../admin/action.xsl"/> 
   
   <xsl:template match="blacklist" name="blacklist">
        
        <!-- Blacklist all the links included in the post. -->
        <xsl:for-each select="/form/content//url">
            <xsl:call-template name="blacklist-url">
                <xsl:with-param name="url" select="."/>
            </xsl:call-template>
        </xsl:for-each>        

    </xsl:template>
    
    <xsl:template name="blacklist-url" >
        <xsl:param name="url"/>
        <!-- Strip the URL down to just the domain -->
        <xsl:variable name="clean-url" select="weblog:normalizeURL($url)"/>
        
        <!-- Make sure it's not already on the list. -->
        <xsl:variable name="query">/blacklist[url = '<xsl:value-of select="$clean-url"/>']</xsl:variable>
        <xsl:if test="not(dbxsl:xpathQuery($config, $query))">
            <!-- Add it to the list -->
            <xsl:variable name="entry">
                <blacklist><url><xsl:value-of select="$clean-url"/></url></blacklist>
            </xsl:variable>
            
            <xsl:call-template name="add">
                <xsl:with-param name="entry" select="$entry"/>
            </xsl:call-template>
        </xsl:if>
    </xsl:template>
    
</xsl:stylesheet>

