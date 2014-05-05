# coding: utf-8
import PIL
from lxml import etree, html
from grokcore.component import adapter, implementer
import zeit.content.article.edit.interfaces
import zeit.content.image.interfaces
import zope.interface
import logging


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


class IFrontendHeaderBlock(zope.interface.Interface):

    """ A HeaderBlock identifies elements that appear only in headers of
    the content.
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
    if obj is None:
        return "no_block"
    return type(obj).__name__.lower()


@implementer(IFrontendBlock)
@adapter(zeit.content.article.edit.interfaces.IParagraph)
class Paragraph(object):

    def __init__(self, model_block):
        self.html = _inline_html(model_block.xml)

    def __str__(self):
        return unicode(self.html)

@implementer(IFrontendBlock)
@adapter(zeit.content.article.edit.interfaces.IPortraitbox)
class Portraitbox(object):

    def __init__(self, model_block):
        self.text = self._author_text(model_block.references.text)
        self.name = model_block.references.name

    def _author_text(self, pbox):
        # TODO: Highly fragile, we need to find a better solution
        # Apparently we don't have a root element
        p_text = html.fragments_fromstring(pbox)[0]
        return etree.tostring(p_text)

class BaseImage(object):

    @property
    def ratio(self):
        width, height = PIL.Image.open(self.image.open()).size
        return float(width) / float(height)


@implementer(IFrontendBlock)
@adapter(zeit.content.article.edit.interfaces.IImage)
class Image(BaseImage):

    def __new__(cls, model_block):
        if (model_block.layout == 'zmo-xl-header' or
                getattr(model_block, 'is_empty', False)):
            return None
        return super(Image, cls).__new__(cls, model_block)

    def __init__(self, model_block):
        # TODO: don't use XML but adapt an Image and use it's metadata
        xml = model_block.xml
        self.align = xml.get('align')
        self.caption = _inline_html(xml.find('bu'))
        self.copyright = _inline_html(xml.find('copyright'))
        self.layout = model_block.layout
        if model_block.references:
            self.image = model_block.references.target
            self.src = self.image and self.image.uniqueId
            self.uniqueId = self.image and self.image.uniqueId
            self.attr_title = model_block.references.title
            self.attr_alt = model_block.references.alt
        else:
            self.image = None
            self.src = None
            self.attr_title = None
            self.attr_alt = None


@implementer(IFrontendHeaderBlock)
@adapter(zeit.content.article.edit.interfaces.IImage)
class HeaderImage(Image):

    def __new__(cls, model_block):
        if (model_block.layout != 'zmo-xl-header' or
                getattr(model_block, 'is_empty', False)):
            return None
        return super(Image, cls).__new__(cls, model_block)

    def __init__(self, model_block):
        super(HeaderImage, self).__init__(model_block)


@implementer(IFrontendHeaderBlock)
@adapter(zeit.content.article.edit.interfaces.IImage)
class HeaderImageStandard(HeaderImage):
    pass


@implementer(IFrontendBlock)
@adapter(zeit.content.article.edit.interfaces.IIntertitle)
class Intertitle(object):

    def __init__(self, model_block):
        self.text = unicode(model_block.text)

    def __str__(self):
        return self.text


@implementer(IFrontendBlock)
@adapter(zeit.content.article.edit.interfaces.IRawXML)
class Raw(object):

    def __init__(self, model_block):
        self.xml = _raw_html(model_block.xml)


@implementer(IFrontendBlock)
@adapter(zeit.content.article.edit.interfaces.ICitation)
class Citation(object):

    def __init__(self, model_block):
        self.url = model_block.url
        self.attribution = model_block.attribution
        self.text = model_block.text
        self.layout = model_block.layout


class _Video(object):

    def __init__(self, model_block):
        if getattr(model_block, 'video', None) is None:
            return None
        self.renditions = model_block.video.renditions
        self.video_still = model_block.video.video_still
        self.description = model_block.video.subtitle
        self.title = model_block.video.title
        self.id = model_block.video.uniqueId.split('/')[-1]  # XXX ugly
        self.format = model_block.layout

    @property
    def source(self):
        try:
            highest_rendition = self.renditions[0]
            for rendition in self.renditions:
                if highest_rendition.frame_width < rendition.frame_width:
                    highest_rendition = rendition
            return highest_rendition.url
        except AttributeError:
            logging.exception("no renditions set")
        except TypeError:
            logging.exception("renditions are propably empty")


@implementer(IFrontendBlock)
@adapter(zeit.content.article.edit.interfaces.IVideo)
class Video(_Video):

    def __new__(cls, model_block):
        if model_block.layout == 'zmo-xl-header':
            return None
        return super(Video, cls).__new__(cls, model_block)

    def __init__(self, model_block):
        super(Video, self).__init__(model_block)


@implementer(IFrontendHeaderBlock)
@adapter(zeit.content.article.edit.interfaces.IVideo)
class HeaderVideo(_Video):

    def __new__(cls, model_block):
        if model_block.layout != 'zmo-xl-header':
            return None
        return super(HeaderVideo, cls).__new__(cls, model_block)

    def __init__(self, model_block):
        super(HeaderVideo, self).__init__(model_block)


class InlineGalleryImage(Image):

    def __init__(self, item):
        self.caption = item.caption
        self.layout = "large"  # item.layout
        self.title = item.title
        self.text = item.text

        if hasattr(item, 'image'):
            self.src = item.image.uniqueId
            self.uniqueId = item.image.uniqueId
            self.image = item.image
        image_meta = zeit.content.image.interfaces.IImageMetadata(item)
        # TODO: get complete list of copyrights with links et al
        # this just returns the first copyright without link
        # mvp it is
        self.copyright = [copyright[0]
                          for copyright in image_meta.copyrights][0]
        self.alt = image_meta.alt
        self.align = image_meta.alignment


@implementer(IFrontendBlock)
@adapter(zeit.content.article.edit.interfaces.IGallery)
class InlineGallery(object):

    def __init__(self, model_block):
        self._gallery_items = model_block.references.items

    def items(self):
        my_items = []
        for item in self._gallery_items():
            src, entry = item
            if(entry.layout != 'hidden'):
                my_items.append(InlineGalleryImage(entry))
        return my_items


def _raw_html(xml):
    filter_xslt = etree.XML('''
        <xsl:stylesheet version="1.0"
            xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
            <xsl:output method="xml"
                        omit-xml-declaration="yes" />
          <xsl:template match="raw">
            <xsl:copy-of select="*" />
          </xsl:template>
        </xsl:stylesheet>
    ''')
    transform = etree.XSLT(filter_xslt)
    return transform(xml)


def _inline_html(xml):
    allowed_elements = "a|span|strong|img|em|sup|sub|caption|br"
    filter_xslt = etree.XML('''
        <xsl:stylesheet version="1.0"
            xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
            <xsl:output method="xml"
                        omit-xml-declaration="yes" />
          <!-- Semantische HTML-ELemente übernehmen -->
          <xsl:template match="%s">
          <xsl:element name="{name()}">
            <xsl:apply-templates select="@*" />
            <xsl:apply-templates select="*|text()[normalize-space(.) != '']" />
          </xsl:element>
          </xsl:template>
          <xsl:template match="@abbr|@accept|@accept-charset|@accesskey|
                               @action|@alt|@async|@autocomplete|@autofocus|
                               @autoplay|@challenge|@charset|@checked|@cite|
                               @class|@cols|@colspan|@command|@content|
                               @contenteditable|@contextmenu|@controls|
                               @coords|@crossorigin|@data|@datetime|
                               @default|@defer|@dir|@dirname|@disabled|
                               @draggable|@dropzone|@enctype|@for|@form|
                               @formaction|@formenctype|@formmethod|
                               @formnovalidate|@formtarget|@headers|
                               @height|@hidden|@high|@href|@hreflang|
                               @http-equiv|@icon|@id|@inert|@inputmode|
                               @ismap|@itemid|@itemprop|@itemref|
                               @itemscope|@itemtype|@keytype|@kind|@label|
                               @lang|@list|@loop|@low|@manifest|@max|
                               @maxlength|@media|@mediagroup|@method|
                               @min|@multiple|@muted|@name|@novalidate|
                               @onabort|@onafterprint|@onbeforeprint|
                               @onbeforeunload|@onblur|@onblur|@oncanplay|
                               @oncanplaythrough|@onchange|@onclick|
                               @oncontextmenu|@ondblclick|@ondrag|
                               @ondragend|@ondragenter|@ondragleave|
                               @ondragover|@ondragstart|@ondrop|
                               @ondurationchange|@onemptied|@onended|
                               @onerror|@onfocus|@onformchange|
                               @onforminput|@onhashchange|@oninput|
                               @oninvalid|@onkeydown|@onkeypress|
                               @onkeyup|@onload|@onloadeddata|
                               @onloadedmetadata|@onloadstart|
                               @onmessage|@onmousedown|@onmousemove|
                               @onmouseout|@onmouseover|@onmouseup|
                               @onmousewheel|@onoffline|@ononline|
                               @onpagehide|@onpageshow|@onpause|
                               @onplay|@onplaying|@onpopstate|
                               @onprogress|@onratechange|@onreadystatechange|
                               @onreset|@onresize|@onscroll|@onseeked|
                               @onseeking|@onselect|@onshow|@onstalled|
                               @onstorage|@onsubmit|@onsuspend|
                               @ontimeupdate|@onunload|@onvolumechange|
                               @onwaiting|@open|@optimum|@option|@pattern|
                               @ping|@placeholder|@poster|@preload|
                               @pubdate|@radiogroup|@readonly|@readonly|
                               @rel|@required|@reversed|@role|@rows|
                               @rowspan|@sandbox|@scope|@scoped|@seamless|
                               @selected|@shape|@size|@sizes|@span|
                               @spellcheck|@src|@srcdoc|@srclang|@srcset|
                               @start|@step|@style|@tabindex|@target|
                               @title|@translate|@type|@typemustmatch|
                               @usemap|@value|@width|@wrap|
                               @*[starts-with(name(),'data-')]|
                               @*[starts-with(name(),'aria-')]">
              <xsl:attribute name="{name()}">
                <xsl:value-of select="." />
              </xsl:attribute>
            </xsl:template>
          <xsl:template match="@*" />
        </xsl:stylesheet>''' % (allowed_elements))
    try:
        transform = etree.XSLT(filter_xslt)
        return transform(xml)
    except TypeError:
        return None
