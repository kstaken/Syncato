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
                                
                <xsl:call-template name="url-list"> 
                    <xsl:with-param name="urls" select="node()/url | comment/body//@href | comment/body//@HREF"/>
                    <xsl:with-param name="type">comment</xsl:with-param>
                </xsl:call-template>
                
            </div>
            
            <xsl:call-template name="copyright"/>    
        </div>
    </xsl:template>      
    
    <xsl:template name="form">
        <div id="form">
        <form method="post" action="{$config/admin-url}">
            <div class="button-group">
            <input type="hidden" name="type" value="comment"/>
            <input type="submit" name="button/delete" value="Delete"/>
            
            <input type="submit" name="button/delete-and-blacklist" value="Delete and Blacklist all URLs"/>
                                    
            <input type="submit" name="button/save" value="Save" class="pad-left" />
            
            <input type="hidden" name="@id" value="{node()/@id}"/>
            <input type="hidden" name="action/delete" value="{$config/admin-url}/collection/comment"/>
            <input type="hidden" name="action/save" value="{$config/admin-url}/collection/comment"/>
            <input type="hidden" name="action/delete-and-blacklist" value="{$config/admin-url}/collection/comment"/>
            
            <input type="hidden" name="action/error" value="comment/editor"/>
            
            </div>
            <div class="form">
                
                Author:<br />
                <input name="/comment/author" size="80" value="{comment/author}"/><br /><br />
               
                URL:<br />
                <input name="/comment/url" size="80" value="{comment/url}"/><br /><br />
                
                Comments:<br />
                <textarea name="/comment/body#markup" rows="15" cols="80"><xsl:value-of select="weblog:serialize(comment/body/node())" disable-output-escaping="yes"/></textarea><br /><br />
                <input type="hidden" name="#required#/comment/body" value="Some comment text is required."/>
                
            </div>
            
        </form>
        
        </div>
    </xsl:template>
    
</xsl:stylesheet>

