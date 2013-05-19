<xsl:stylesheet
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
        xmlns:dbxml="http://www.sleepycat.com/2002/dbxml"
        xmlns:date="http://exslt.org/dates-and-times"
        xmlns:weblog="http://www.xmldatabases.org/weblog"        
        xmlns:dbxsl="http://www.xmldatabases.org/dbxsl"
        extension-element-prefixes="dbxsl weblog"
        xsl:version="1.0">
        
    <xsl:template name="url-list">
        <xsl:param name="urls"/>
        <xsl:param name="type"/>
        
        <form method="post" action="{$config/admin-url}/blacklist">
            <div class="button-group">
                <input type="submit" name="button/blacklist" value="Blacklist Selected URLs" class="pad-left"/>
                <input type="hidden" name="@id" value="{node()/@id}"/>
                <input type="hidden" name="type" value="blacklist"/>
                <input type="hidden" name="action/blacklist" value="{$config/admin-url}/collection/{$type}"/>
            
                <input type="hidden" name="action/error" value="comment/{$type}"/>            
            </div>
                          
            <table class="collection">
                <tr>
                    <th>URL</th>
                    <th>Add To Blacklist</th>
                </tr>
                
                <xsl:for-each select="$urls">
                    
                    <xsl:variable name="style">
                        <xsl:choose>
                            <xsl:when test="position() mod 2 = 0">row-plain</xsl:when>
                            <xsl:otherwise>row-color</xsl:otherwise>
                        </xsl:choose>
                    </xsl:variable>
                    
                    <tr class="{$style}">
                        <td>
                            <xsl:value-of select="."/>
                        </td>
                        <td align="center">
                            <input type="checkbox" name="/blacklist/url" value="{.}" />
                        </td>
                   </tr>
          
                </xsl:for-each>
                
            </table>
        </form>
    </xsl:template>
</xsl:stylesheet>
