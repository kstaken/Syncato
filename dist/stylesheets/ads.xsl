<!-- The templates in this file can be used to insert Amazon associates and Google AdSense ads into pages. -->

<xsl:stylesheet
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
        xsl:version="1.0">
    
    <!-- Insert links for Amazon products -->
    <xsl:template match="asin">
        <xsl:variable name="asin"><xsl:value-of select="."/></xsl:variable>
                
        <iframe marginwidth="0" marginheight="0" width="120" height="240" scrolling="no" frameborder="0" src="http://rcm.amazon.com/e/cm?o=1&amp;l=as1&amp;f=ifr&amp;t={$config/amazon-associates-id}&amp;p=8&amp;asins={$asin}&amp;IS2=1&amp;amp;lt1=_blank">
            <map NAME="boxmap-p8">
                <area SHAPE="RECT" COORDS="14, 200, 103, 207" HREF="http://rcm.amazon.com/e/cm/privacy-policy.html?o=1" ></area>
                <area COORDS="0,0,10000,10000" HREF="http://www.amazon.com/exec/obidos/redirect-home/inspiration08-20" ></area>
            </map>
            <img src="http://rcm-images.amazon.com/images/G/01/rcm/120x240.gif" width="120" height="240" border="0" usemap="#boxmap-p8" alt="Shop at Amazon.com" />
        </iframe>
        
    </xsl:template>
    
    <xsl:template name="amazon-skyscraper">
        <xsl:param name="query"/>
        <div id="floating-ad-right">
        <iframe marginwidth="0" marginheight="0" width="160" height="600" scrolling="no" frameborder="0" src="http://rcm.amazon.com/e/cm?t={$config/amazon-associates-id}&amp;l=st1&amp;search={$query}&amp;mode=books&amp;p=14&amp;o=1&amp;lt1=_blank&amp;f=ifr">

            <MAP NAME="boxmap-p14">
                <AREA SHAPE="RECT" COORDS="37, 588, 126, 600" HREF="http://rcm.amazon.com/e/cm/privacy-policy.html?o=1" target="main" /> 
                <AREA COORDS="0,0,10000,10000" HREF="http://www.amazon.com/exec/obidos/redirect-home/inspiration08-20" target="main" />
            </MAP>
            <img src="http://rcm-images.amazon.com/images/G/01/rcm/160x600.gif" width="160" height="600" border="0" usemap="#boxmap-p14" alt="Shop at Amazon.com" />

        </iframe>
        </div>
    </xsl:template>
    
    
    <xsl:template name="amazon-box">
        <iframe width="120" height="240" scrolling="no" frameborder="0" src="http://rcm.amazon.com/e/cm?t={$config/amazon-associates-id}&amp;p=8&amp;o=1&amp;l=ez&amp;f=ifr">
            
            <MAP NAME="boxmap-p8">
                <AREA SHAPE="RECT" COORDS="14, 200, 103, 207" HREF="http://rcm.amazon.com/e/cm/privacy-policy.html?o=1" />
                <AREA COORDS="0,0,10000,10000" HREF="http://www.amazon.com/exec/obidos/redirect-home/inspiration08-20" />
            </MAP>
            <img src="http://rcm-images.amazon.com/images/G/01/rcm/120x240.gif" width="120" height="240" border="0" usemap="#boxmap-p8" alt="Shop at Amazon.com" />
            
        </iframe>
    </xsl:template>
    
    <xsl:template name="google-skyscraper">
        <div id="floating-ad-right">
        <script type="text/javascript"><xsl:comment><![CDATA[
        google_ad_client = "]]><xsl:value-of select="$config/google-ad-id"/><![CDATA[";
        
        google_ad_width = 120;
        google_ad_height = 600;
        google_ad_format = '120x600_as';
        //]]>
        </xsl:comment></script>
        <script type="text/javascript"
          src="http://pagead2.googlesyndication.com/pagead/show_ads.js"> <xsl:text> </xsl:text>
        </script>
        </div>
    </xsl:template>
    
    <xsl:template name="google-banner">
        <div align="center">
            <script type="text/javascript"><xsl:comment><![CDATA[
            google_ad_client = "]]><xsl:value-of select="$config/google-ad-id"/><![CDATA[";
google_ad_width = 728;
google_alternate_ad_url = "http://www.alternateurl.com/show?memid=872&size=728x90";
google_ad_height = 90;
google_ad_format = "728x90_as";
google_ad_type = "text_image";
google_color_border = "D9D9D9";
google_color_bg = "D9D9D9";
google_color_link = "3D00FF";
google_color_url = "3D00FF";
google_color_text = "000000";
            //google_ad_width = 468;
            //google_ad_height = 60;
            //google_ad_format = "468x60_as";
            //google_color_border = "CCCCCC";
            //google_color_bg = "FFFFFF";
            //google_color_link = "000000";
            //google_color_url = "666666";
            //google_color_text = "333333";
            //]]></xsl:comment></script>
            
            <script type="text/javascript"
              src="http://pagead2.googlesyndication.com/pagead/show_ads.js"><xsl:text> </xsl:text>
            </script>
        </div>
    </xsl:template>
    
    <xsl:template name="google-links">
        <div id="floating-ad-right">
            <script type="text/javascript"><xsl:comment><![CDATA[
            google_ad_client = "]]><xsl:value-of select="$config/google-ad-id"/><![CDATA[";
google_ad_width = 728;
google_ad_height = 15;
google_ad_format = "728x15_0ads_al_s";
google_ad_channel ="";
google_color_border = "D9D9D9";
google_color_bg = "D9D9D9";
google_color_link = "3D00FF";
google_color_url = "3D00FF";
google_color_text = "000000";
            //]]></xsl:comment></script>

            <script type="text/javascript"
              src="http://pagead2.googlesyndication.com/pagead/show_ads.js"><xsl:text> </xsl:text>
            </script>
        </div>
    </xsl:template>

    <xsl:template name="google-inline">
        <div id="floating-ad-right">
            <script type="text/javascript"><xsl:comment><![CDATA[
            google_ad_client = "]]><xsl:value-of select="$config/google-ad-id"/><![CDATA[";
            google_ad_width = 300;
            google_ad_height = 250;
            google_ad_format = "300x250_as";
            google_color_border = "CCCCCC";
            google_color_bg = "FFFFFF";
            google_color_link = "000000";
            google_color_url = "666666";
            google_color_text = "333333";
            //]]></xsl:comment></script>
            
            <script type="text/javascript"
              src="http://pagead2.googlesyndication.com/pagead/show_ads.js"><xsl:text> </xsl:text>
            </script>
        </div>
    </xsl:template>
</xsl:stylesheet>
