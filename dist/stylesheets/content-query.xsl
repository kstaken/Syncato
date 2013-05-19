<xsl:stylesheet
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
        xmlns:dbxml="http://www.sleepycat.com/2002/dbxml"
        xmlns:date="http://exslt.org/dates-and-times"
        xmlns:weblog="http://www.xmldatabases.org/weblog"        
        xmlns:dbxsl="http://www.xmldatabases.org/dbxsl"
        extension-element-prefixes="dbxsl weblog"
        xsl:version="1.0">
        
    <!-- Read in the configuration so that we can set properties in the stylesheet -->
    <xsl:variable name="config" select="document('../../config/config.xml')/blog"/>
    
    <xsl:template match="/">
        <html>  
        <head>
            <link rel="stylesheet" type="text/css" href="{$config/content-url}/{$config/css-style}"/>
        </head>
        
        <body>
            <xsl:apply-templates select="/results"/>
        </body>
        </html>
    </xsl:template>
     
    <!-- identity transform to copy through everything by default -->   
    <xsl:template match="node()|@*">
        <xsl:copy><xsl:apply-templates select="@*"/><xsl:apply-templates/></xsl:copy>
    </xsl:template>
</xsl:stylesheet>

