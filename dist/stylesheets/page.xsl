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
 
    <xsl:template name="content-body">
        <xsl:apply-templates select="//page/body/node()">
            <xsl:sort select="pubDate/@seconds" data-type="number" order="descending"/>
        </xsl:apply-templates>
    </xsl:template>
    
    <xsl:template name="links">            
        <xsl:apply-templates select="//page/sidebar"/>
    </xsl:template>
    
    <xsl:template name="banner">
        <div id="banner">
            <h1>
            <a href="{$config/base-url}/{//page/@id}?t=page">
                <xsl:value-of select="//page/title"/>
            </a>
            </h1>
            <span class="description"><xsl:value-of select="//page/description"/></span>
        </div>
    </xsl:template>    
    
    <xsl:template match="sidebar">
        <div id="links">
            <xsl:apply-templates/>             
        </div>
    </xsl:template>
    
</xsl:stylesheet>

