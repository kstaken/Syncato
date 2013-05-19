<xsl:stylesheet
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
        xmlns:dbxml="http://www.sleepycat.com/2002/dbxml"
        xsl:version="1.0">
    
    <xsl:template match="/">
        <xsl:apply-templates/>
    </xsl:template>
    
    <xsl:template match="/results/item">
        <item>
            <xsl:attribute name="id"><xsl:value-of select="@dbxml:id"/></xsl:attribute>
            <xsl:apply-templates/>
        </item>
    </xsl:template>
    
    <!-- identity transform to copy through everything by default -->   
    <xsl:template match="node()|@*">
        <xsl:copy><xsl:apply-templates select="@*"/><xsl:apply-templates/></xsl:copy>
    </xsl:template>
</xsl:stylesheet>