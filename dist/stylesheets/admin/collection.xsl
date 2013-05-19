<xsl:stylesheet
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
        xmlns:dbxml="http://www.sleepycat.com/2002/dbxml"
        xmlns:date="http://exslt.org/dates-and-times"
        xmlns:dyn="http://exslt.org/dynamic"
        xmlns:weblog="http://www.xmldatabases.org/weblog"        
        xmlns:dbxsl="http://www.xmldatabases.org/dbxsl"
        extension-element-prefixes="dbxsl weblog"
        xsl:version="1.0">
    <xsl:import href="../admin/edit.xsl"/>  
    
    <xsl:template name="body">
            
        <div id="content">                     
            <div class="blog">
                <div class="blogbody">
                    <form action="{$config/admin-url}" method="POST">
                        <div class="button-group">
                            <input type="submit" name="button/delete-all" value="Delete Selected"/>
                        </div>
                        
                        <input type="hidden" name="type" value="admin"/>
                        
                        <input type="hidden" name="action/delete-all" value="referer"/>
                        
                        <table class="collection">
                            <xsl:call-template name="collection-body"/>                            
                        </table>
                    </form>
                </div>           
            </div>
            
            <xsl:call-template name="copyright"/>
        </div>
    </xsl:template>  
        
    <xsl:template name="collection-body">
        <tr>
            <xsl:apply-templates select="/collection/field"/>            
            <th>Delete</th>
        </tr>
        <xsl:call-template name="collection-table"/>
    </xsl:template>
    
    <xsl:template match="field">
        <th><xsl:value-of select="@title"/></th> 
    </xsl:template>
    
    <xsl:template name="collection-table">
        <xsl:variable name="fields" select="/collection/field"/>
        <xsl:for-each select="dbxsl:xpathQuery($config, /collection/query)">       
            <xsl:sort select="pubDate/@seconds" data-type="number" order="descending"/>
            
            <xsl:variable name="style">
                <xsl:choose>
                    <xsl:when test="position() mod 2 = 0">row-plain</xsl:when>
                    <xsl:otherwise>row-color</xsl:otherwise>
                </xsl:choose>
            </xsl:variable>
            
            <tr class="{$style}">
                <xsl:variable name="result" select="."/>
                <xsl:for-each select="$fields">
                    <td>
                        <xsl:variable name="field">$result/<xsl:value-of select="."/></xsl:variable>
                            
                        <xsl:choose>
                            <xsl:when test="@type = 'date'">
                                <xsl:call-template name="date-format">
                                    <xsl:with-param name="date" select="dyn:evaluate($field)"/>
                                </xsl:call-template>
                            </xsl:when>
                            <xsl:when test="@type = 'link'">
                                <!--xsl:value-of select="blog_name"/> :-->
                                <a href="{dyn:evaluate($field)}" target="_blank">
                                    <xsl:value-of select="dyn:evaluate($field)"/>
                                </a>
                            </xsl:when>
                            <xsl:when test="@type = 'id-summary-link'">
                                <a href="{$config/base-url}/{dyn:evaluate('$result/@id')}?t={@style}">
                                    <xsl:choose>
                                        <xsl:when test="dyn:evaluate($field)">
                                            <xsl:value-of select="weblog:summarize(dyn:evaluate($field), 20)"/>
                                        </xsl:when>
                                        <xsl:otherwise>No content</xsl:otherwise>
                                    </xsl:choose>
                                </a>
                            </xsl:when>
                            <xsl:when test="@type = 'id-link'">
                                <a href="{$config/base-url}/{dyn:evaluate('$result/@id')}?t={@style}">
                                    <xsl:choose>
                                        <xsl:when test="dyn:evaluate($field)">
                                            <xsl:value-of select="dyn:evaluate($field)"/>
                                        </xsl:when>
                                        <xsl:otherwise>No content</xsl:otherwise>
                                    </xsl:choose>
                                </a>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:value-of select="dyn:evaluate($field)"/>
                            </xsl:otherwise>
                        </xsl:choose>
                    </td>
                </xsl:for-each>
                
                <td></td>
                <td>
                    <input type="checkbox" name="/delete/id" value="{@id}" />
                </td>              
            </tr>
            
       </xsl:for-each>
    </xsl:template>
</xsl:stylesheet>