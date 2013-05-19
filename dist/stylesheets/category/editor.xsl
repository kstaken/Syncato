<xsl:stylesheet
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
        xmlns:dbxml="http://www.sleepycat.com/2002/dbxml"
        xmlns:date="http://exslt.org/dates-and-times"
        xmlns:weblog="http://www.xmldatabases.org/weblog"        
        xmlns:dbxsl="http://www.xmldatabases.org/dbxsl"
        extension-element-prefixes="dbxsl weblog"
        xsl:version="1.0">
    <xsl:import href="../admin/edit.xsl"/> 
    <xsl:import href="../blacklist/editor.xsl"/>     
        
    <xsl:template name="body">            
        <div id="content">                     
            <div class="blog">
                <div class="blogbody">
                    <xsl:call-template name="error"/>
                    
                    <xsl:call-template name="form"/>
                </div>                
            </div>
            
            <xsl:call-template name="copyright"/>    
        </div>
    </xsl:template>      
    
    <xsl:template name="form">
        <div id="form">
        <form method="post" action="{$config/admin-url}">
            <div class="button-group">
            <input type="hidden" name="type" value="category"/>
            <xsl:if test="category-def">
                <input type="submit" name="button/delete" value="Delete"/>
            </xsl:if>
                                
            <input type="submit" name="button/save" value="Save" class="pad-left" />
            
            <input type="hidden" name="@id" value="{node()/@id}"/>
            <input type="hidden" name="action/delete" value="{$config/admin-url}/collection/category"/>
            <input type="hidden" name="action/save" value="{$config/admin-url}/collection/category"/>
            <input type="hidden" name="action/delete-and-blacklist" value="{$config/admin-url}/collection/category"/>
            
            <input type="hidden" name="action/error" value="category/editor"/>
            
            </div>
            <div class="form">
                Category name:<br />
                <input name="/category-def/title" size="80" value="{category-def/title}"/><br /><br />
                <input type="hidden" name="#required#/category-def/title" value="A title is required"/>
                
                Desciption:<br />
                <input name="/category-def/description" size="80" value="{category-def/description}"/><br /><br />
                
            </div>
                        
        </form>
        
        </div>
    </xsl:template>
        
</xsl:stylesheet>

