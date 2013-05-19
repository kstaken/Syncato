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
            <input type="hidden" name="type" value="page"/>
            <xsl:if test="page">
                <input type="submit" name="button/delete" value="Delete"/>
            </xsl:if>
                                
            <input type="submit" name="button/save" value="Save" class="pad-left" />
            
            <input type="hidden" name="@id" value="{node()/@id}"/>
            <input type="hidden" name="action/delete" value="{$config/admin-url}/collection/page"/>
            <input type="hidden" name="action/save" value="{$config/admin-url}/collection/page"/>
            
            <input type="hidden" name="action/error" value="page/editor"/>
            
            </div>
            <div class="form">
                Page name:<br />
                <input name="/page/@name" size="80" value="{page/@name}"/><br /><br />
                <input type="hidden" name="#required#/page/@name" value="You must provide a name for the page"/>
                
                Page title:<br/>
                <input name="/page/title" size="80" value="{page/title}"/><br /><br />
                <input type="hidden" name="#required#/page/title" value="A title is required"/>
                
                Body:<br />
                <textarea name="/page/body#markup" rows="15" cols="80"><xsl:value-of select="weblog:serialize(page/body/node())" disable-output-escaping="yes"/></textarea><br /><br />
                
            </div>
                        
        </form>
        
        </div>
    </xsl:template>
        
</xsl:stylesheet>

