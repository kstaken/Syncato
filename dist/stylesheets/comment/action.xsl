<xsl:stylesheet
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
        xmlns:dbxml="http://www.sleepycat.com/2002/dbxml"
        xmlns:date="http://exslt.org/dates-and-times"
        xmlns:weblog="http://www.xmldatabases.org/weblog"        
        xmlns:dbxsl="http://www.xmldatabases.org/dbxsl"
        extension-element-prefixes="dbxsl weblog"
        xsl:version="1.0">
    <xsl:import href="../admin/action.xsl"/> 
    <xsl:import href="../blacklist/action.xsl"/> 
    
    <xsl:template match="delete-and-blacklist" name="delete-and-blacklist">
        <!-- Blacklist the URL field -->
        <xsl:call-template name="blacklist-url">
            <xsl:with-param name="url" select="//url"/>
        </xsl:call-template>
        
        <!-- Blacklist all the links included in the post. -->
        <xsl:for-each select="/form/content//a/@href">
            <xsl:call-template name="blacklist-url">
                <xsl:with-param name="url" select="."/>
            </xsl:call-template>
        </xsl:for-each>
        
        <!-- Delete the entry -->
        <xsl:call-template name="delete">
            <xsl:with-param name="entryID" select="/form/@id"/>
        </xsl:call-template>
    </xsl:template>
    
</xsl:stylesheet>

