<xsl:stylesheet
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
        xmlns:dbxml="http://www.sleepycat.com/2002/dbxml"
        xmlns:date="http://exslt.org/dates-and-times"
        xmlns:weblog="http://www.xmldatabases.org/weblog"        
        xmlns:dbxsl="http://www.xmldatabases.org/dbxsl"
        extension-element-prefixes="dbxsl weblog"
        xsl:version="1.0">
        
    <xsl:import href="../admin/edit.xsl"/>
    
    <xsl:template name="body">
        <form method="post" action="{$config/admin-url}?type=item">
            
        <div id="content">                     
            <div class="blog">
                <div class="blogbody">
                    <div class="button-group">
                        <input type="submit" name="button/preview" value="Preview" />
                        <input type="submit" name="button/save" value="Post" />
                        <input type="hidden" name="@id" value="{item/@id}"/>      
                        <input type="hidden" name="action/save" value="item/editor"/>
            
                        <input type="hidden" name="action/error" value="item/editor"/>
                        <input type="hidden" name="action/preview" value="item/editor"/>                                          
                    </div>
                    
                    <div class="form">
                    <table>
                        <tr>
                        <td>
                            <div id="form">
                                Title:<br />
                                <input name="/item/title" size="80" value="{item/title}"/><br /><br />
                                <input type="hidden" name="#required#/item/title" value="You must provide a title for the post."/>
                                
                                
                                Body:<br />
                                <textarea name="/item/description#markup" rows="15" cols="80"><xsl:value-of select="weblog:serialize(item/description/node())" disable-output-escaping="yes"/></textarea><br /><br />
                                
                            </div>
                        </td>
                        <td valign="top">                                    
                            Categories:<br />
                            <xsl:call-template name="category-list"/>
                        </td>
                        </tr>
                        
                    </table>
                    </div>

                </div>
                
                <xsl:call-template name="item"/>
            </div>

            <xsl:call-template name="copyright"/>   
        </div>
            
        </form>  
    </xsl:template>      
    
    <xsl:template name="item">
        <xsl:call-template name="error"/>
        
        <div class="comments-title">
        Preview
        </div>
        
        <xsl:apply-templates select="/item"/>
         
    </xsl:template>
        
    <xsl:template name="category-list">
        <xsl:variable name="categories" select="/item/category"/>
        
        <xsl:for-each select="dbxsl:xpathQuery($config, '/category-def')">  
            <xsl:variable name="id" select="title"/> 
            
            <input name="/item/category" type="checkbox" value="{$id}">
                <xsl:for-each select="$categories">
                    <xsl:if test="text() = $id">
                        <xsl:attribute name="checked"/>
                    </xsl:if>
                </xsl:for-each>
            </input> 
            
            <xsl:value-of select="title"/><br />
        </xsl:for-each>
        
        <!-- This hidden field enables all categories
        to be un-selected and for the document to get properly updated -->
        <input type="hidden" name="#marker#/item/category" value="#marker"/>
    </xsl:template>
</xsl:stylesheet>
