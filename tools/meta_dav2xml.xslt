<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:D="DAV:" 
  >

  <xsl:template match="/">
  <head>
    <xsl:apply-templates select="D:multistatus/D:response[1]"/>
  </head>
  </xsl:template>

  <xsl:template match="D:response">
    <xsl:apply-templates select="D:href" />
    <xsl:apply-templates select="D:propstat/D:prop" />
    <xsl:apply-templates select="D:propstat/D:prop//rankedTags" />
  </xsl:template>

  <xsl:template match="D:href">
    <xsl:call-template name="attribute" />
  </xsl:template>

  <xsl:template match="D:response/*">
    <xsl:call-template name="attribute" />
  </xsl:template>

  <xsl:template match="D:prop/*[not(rankedTags)]">
    <xsl:call-template name="attribute" />
  </xsl:template>

  <xsl:template match="D:prop//rankedTags">
    <rankedTags>
      <xsl:attribute name="ns">
        <xsl:value-of select ="namespace-uri()" />
      </xsl:attribute>
      <xsl:apply-templates />
    </rankedTags>
  </xsl:template>

  <xsl:template name="attribute">
    <attribute>
      <xsl:attribute name="ns">
        <xsl:value-of select ="namespace-uri()" />
      </xsl:attribute>
      <xsl:attribute name="name">
        <xsl:value-of select="substring-after(name(.),':')" />
      </xsl:attribute>
      <xsl:choose>
        <xsl:when test="starts-with(., '||ESCAPE||')">
          <xsl:value-of select="substring-after(.,'||ESCAPE||')" />
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="." />
        </xsl:otherwise>
      </xsl:choose>
    </attribute>
  </xsl:template>

  <xsl:template match="//rankedTags/tag">
    <tag>
      <xsl:value-of select="." />
    </tag>
  </xsl:template>

</xsl:stylesheet> 

