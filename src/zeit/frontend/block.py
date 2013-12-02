# coding: utf-8
from lxml import etree
from zope.component import adapter
from zope.interface import implementer
import zeit.content.article.edit.interfaces
import zope.interface


# Since this interface is an implementation detail rather than part of the API
# of zeit.frontend, it makes more sense to keep it within the Python module
# that deals with the concept of blocks rather than within a separate
# interfaces module.
class IFrontendBlock(zope.interface.Interface):
    """An item that provides data from an article-body block to a Jinja macro.

    This interface is both a marker for identifying front-end objects
    representing blocks, and a mechanical detail of using the ZCA to construct
    such a front-end representation of a given vivi article-body block.

    """


# Vorläufige Konvention: Die Frontend-Repräsentation eines Blocks
# implementiert IFrontendBlock, und der kleingeschriebene Klassenname ist
# gerade die Typ-Kennung, auf die article.html in der Fallunterscheidung für
# das Macro prüft. Die Fallunterscheidung sollte idealerweise wegfallen, und
# die Macros sollten durch die IFrontendBlock-Objekte selbst festgelegt
# werden. Das API jedes der BlockItem-Objekte muß ja ohnehin zum jeweiligen
# Macro passen.
def is_block(obj, b_type):
    o_type = block_type(obj)
    return IFrontendBlock.providedBy(obj) and o_type == b_type


def block_type(obj):
    return type(obj).__name__.lower()


@implementer(IFrontendBlock)
@adapter(zeit.content.article.edit.interfaces.IParagraph)
class P(object):

    def __init__(self, model_block):
        self.html = _inline_html(model_block.xml)

    def __str__(self):
        return unicode(self.html)


@implementer(IFrontendBlock)
@adapter(zeit.content.article.edit.interfaces.IImage)
class Image(object):

    def __new__(cls, model_block):
        if model_block.layout == 'zmo_header':
            return None
        return super(Image, cls).__new__(cls, model_block)

    def __init__(self, model_block):
        xml = model_block.xml
        self.src = xml.get('src')
        self.align = xml.get('align')
        self.caption = _inline_html(xml.find('bu'))
        self.copyright = _inline_html(xml.find('copyright'))
        self.layout = model_block.layout


@implementer(IFrontendBlock)
@adapter(zeit.content.article.edit.interfaces.IIntertitle)
class Intertitle(object):

    def __init__(self, model_block):
        self.text = unicode(model_block.text)

    def __str__(self):
        return self.text


@implementer(IFrontendBlock)
@adapter(zeit.content.article.edit.interfaces.ICitation)
class Citation(object):

    def __init__(self, model_block):
        self.url = model_block.url
        self.attribution = model_block.attribution
        self.text = model_block.text
        self.layout = model_block.layout


# XXX not modelled in vivi
class Advertising(object):

    def __init__(self, xml):
        self.type = unicode(xml.get('type'))

    def __str__(self):
        return self.type


@implementer(IFrontendBlock)
@adapter(zeit.content.article.edit.interfaces.IVideo)
class Video(object):

    def __init__(self, model_block):
        pass


def _inline_html(xml):
    filter_xslt = etree.XML('''
        <xsl:stylesheet version="1.0"
            xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
            <xsl:output method="xml"
                        omit-xml-declaration="yes" />
            <xsl:template match="p">
                <xsl:apply-templates />
            </xsl:template>
            <xsl:template match="i">
                <i><xsl:apply-templates /></i>
            </xsl:template>
            <xsl:template match="em">
                <em><xsl:apply-templates /></em>
            </xsl:template>
            <xsl:template match="a">
                <xsl:text> </xsl:text>
                <a><xsl:apply-templates select="@* | node | text()" /> </a>
            </xsl:template>
            <xsl:template match="a/@href">
                <xsl:copy><xsl:apply-templates /></xsl:copy>
            </xsl:template>
            <xsl:template match="a/@target">
                <xsl:copy><xsl:apply-templates /></xsl:copy>
            </xsl:template>
        </xsl:stylesheet>''')
    transform = etree.XSLT(filter_xslt)
    return transform(xml)


def configure_components():
    zope.component.provideAdapter(P)
    zope.component.provideAdapter(Image)
    zope.component.provideAdapter(Intertitle)
    zope.component.provideAdapter(Citation)
    zope.component.provideAdapter(Video)
