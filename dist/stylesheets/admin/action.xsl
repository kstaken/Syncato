<xsl:stylesheet
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
        xmlns:dbxml="http://www.sleepycat.com/2002/dbxml"
        xmlns:date="http://exslt.org/dates-and-times"
        xmlns:weblog="http://www.xmldatabases.org/weblog"        
        xmlns:dbxsl="http://www.xmldatabases.org/dbxsl"
        extension-element-prefixes="dbxsl weblog"
        xsl:version="1.0">
    <xsl:import href="../admin/edit.xsl"/> 
    
    <xsl:template match="/">
        <results>
            <xsl:apply-templates select="form/button/node()"/>
            <xsl:apply-templates select="form/action"/>
            <xsl:apply-templates select="form/error-text" mode="copy"/>
        </results>
    </xsl:template>
          
    <xsl:template match="delete" name="delete">
        <xsl:param name="entryID" select="string(/form/@id)"/>
        <xsl:variable name="result" 
            select="dbxsl:deleteRecord($config, $entryID)"/>
       
        <xsl:if test="$result != 'success'">
            <error-text>
                <xsl:value-of select="$result"/>
            </error-text>
        </xsl:if>
            
    </xsl:template>
    
    <xsl:template match="delete-all" name="delete-all">
        <xsl:for-each select="/form/content/delete/id">
            <xsl:call-template name="delete">
                <xsl:with-param name="entryID" select="string(.)"/>
            </xsl:call-template>          
        </xsl:for-each>            
    </xsl:template>
    
    <xsl:template match="add" name="add">
        <xsl:param name="entry"/>
        
        <xsl:variable name="result" 
            select="dbxsl:addRecord($config, $entry)"/>
            
        <xsl:if test="$result != 'success'">
            <error-text>
                <xsl:value-of select="$result"/>
            </error-text>
        </xsl:if>
    </xsl:template>
     
    <xsl:template match="update" name="update">
        <xsl:param name="entryID"/>
        <xsl:param name="entry"/>
        
        <xsl:variable name="result" 
            select="dbxsl:updateRecord($config, $entryID, $entry)"/>
            
        <xsl:if test="$result != 'success'">
            <error-text>
                <xsl:value-of select="$result"/>
            </error-text>
        </xsl:if>
    </xsl:template>
    
    <xsl:template match="save" name="save">
        <xsl:param name="entry" select="/form/content/*"/>
        
        <xsl:choose>
            <xsl:when test="/form/@id">
                <xsl:call-template name="update">
                    <xsl:with-param name="entryID" select="/form/@id"/>
                    <xsl:with-param name="entry" select="$entry"/>
                </xsl:call-template>               
            </xsl:when>
            <xsl:otherwise>
                <xsl:call-template name="add">
                    <xsl:with-param name="entry" select="$entry"/>
                </xsl:call-template>      
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template match="action"> 
        <xsl:copy><xsl:apply-templates mode="copy"/></xsl:copy>
    </xsl:template>
    
    <!-- identity transform to copy through everything when the mode is copy -->   
    <xsl:template match="node()|@*" mode="copy">
        <xsl:copy><xsl:apply-templates select="@*"/><xsl:apply-templates mode="copy"/></xsl:copy>
    </xsl:template>
    
    <!-- We only want explicit matches copied through -->   
    <xsl:template match="node()|@*">        
    </xsl:template>
</xsl:stylesheet>

