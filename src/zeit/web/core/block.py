# -*- coding: utf-8 -*-
import logging
import os.path

import grokcore.component
import lxml.etree
import lxml.html
import PIL
import zope.interface

import zeit.content.article.edit.interfaces
import zeit.content.image.interfaces
import zeit.content.video.interfaces
import zeit.magazin.interfaces
import zeit.newsletter.interfaces

import zeit.web
import zeit.web.core.interfaces


class IFrontendBlock(zope.interface.Interface):

    """An item that provides data from an article-body block to a Jinja macro.

    This interface is both a marker for identifying front-end objects
    representing blocks, and a mechanical detail of using the ZCA to construct
    such a front-end representation of a given vivi article-body block.
    """


class IFrontendHeaderBlock(zope.interface.Interface):

    """A HeaderBlock identifies elements that appear only in headers of
    the content.
    """


@zeit.web.register_filter
def block_type(obj):
    """Outputs the class name in lower case format of one or multiple block
    elements.

    :param obj: list, str or tuple
    :rtype: list, str or tuple
    """

    if obj is None:
        return 'no_block'
    elif isinstance(obj, list) or isinstance(obj, tuple):
        return obj.__class__(block_type(o) for o in obj)
    else:
        return type(obj).__name__.lower()


@grokcore.component.implementer(IFrontendBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IParagraph)
class Paragraph(object):

    def __init__(self, model_block):
        self.html = _inline_html(model_block.xml)

    def __str__(self):
        return unicode(self.html)


@grokcore.component.implementer(IFrontendBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IPortraitbox)
class Portraitbox(object):

    def __init__(self, model_block):
        if model_block.references is not None:
            self.text = self._author_text(model_block.references.text)
            self.name = model_block.references.name

    def _author_text(self, pbox):
        # TODO: Highly fragile, we need to find a better solution
        # Apparently we don't have a root element
        p_text = lxml.html.fragments_fromstring(pbox)[0]
        return lxml.etree.tostring(p_text)


@grokcore.component.implementer(IFrontendBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.ILiveblog)
class Liveblog(object):

    def __init__(self, model_block):
        self.blog_id = model_block.blog_id


class BaseImage(object):

    @property
    def ratio(self):
        width, height = PIL.Image.open(self.image.open()).size
        return float(width) / float(height)


@grokcore.component.implementer(IFrontendBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IImage)
class Image(BaseImage):

    def __new__(cls, model_block):
        if (model_block.layout == 'zmo-xl-header' or
                getattr(model_block, 'is_empty', False)):
            return
        return super(Image, cls).__new__(cls, model_block)

    def __init__(self, model_block):
        # TODO: don't use XML but adapt an Image and use it's metadata
        self.layout = model_block.layout

        if model_block.xml is not None:
            self.align = model_block.xml.get('align')
            self.href = model_block.xml.get('href')
            self.caption = _inline_html(model_block.xml.find('bu'))
            cr = model_block.xml.find('copyright')
            rel = cr.attrib.get('rel', '') == 'nofollow'
            self.copyright = ((cr.text, cr.attrib.get('link', None), rel),)
            self.attr_title = _inline_html(model_block.xml.find('bu'))
            self.attr_alt = _inline_html(model_block.xml.find('bu'))

        if model_block.references is not None:
            self.image = model_block.references.target
            self.src = self.image and self.image.uniqueId
            self.uniqueId = self.image and self.image.uniqueId
            if model_block.references.title is not None:
                self.attr_title = model_block.references.title
            if model_block.references.alt is not None:
                self.attr_alt = model_block.references.alt
        else:
            self.image = None
            self.src = None


@grokcore.component.implementer(IFrontendHeaderBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IImage)
class HeaderImage(Image):

    def __new__(cls, model_block):
        if (model_block.layout != 'zmo-xl-header' or
                getattr(model_block, 'is_empty', False)):
            return
        return super(Image, cls).__new__(cls, model_block)

    def __init__(self, model_block):
        super(HeaderImage, self).__init__(model_block)


@grokcore.component.implementer(IFrontendHeaderBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IImage)
class HeaderImageStandard(HeaderImage):
    pass


@grokcore.component.implementer(IFrontendBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IIntertitle)
class Intertitle(object):

    def __init__(self, model_block):
        self.text = unicode(model_block.text)

    def __str__(self):
        return self.text


@grokcore.component.implementer(IFrontendBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IRawXML)
class Raw(object):

    def __init__(self, model_block):
        self.xml = _raw_html(model_block.xml)


@grokcore.component.implementer(IFrontendBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.ICitation)
class Citation(object):

    def __init__(self, model_block):
        self.url = model_block.url
        self.attribution = model_block.attribution
        self.text = model_block.text
        self.layout = model_block.layout


class BaseVideo(object):

    def __init__(self, model_block):
        if getattr(model_block, 'video', None) is None:
            return
        self.renditions = model_block.video.renditions
        self.video_still = model_block.video.video_still
        self.title = model_block.video.title
        self.description = model_block.video.subtitle
        self.title = model_block.video.title
        self.id = model_block.video.uniqueId.split('/')[-1]  # XXX ugly
        self.format = model_block.layout

    @property
    def highest_rendition(self):
        try:
            highest_rendition = self.renditions[0]
            for rendition in self.renditions:
                if highest_rendition.frame_width < rendition.frame_width:
                    highest_rendition = rendition
            return highest_rendition.url
        except AttributeError:
            logging.exception('No renditions set')
        except TypeError:
            logging.exception('Renditions are propably empty')


@grokcore.component.implementer(IFrontendBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IVideo)
class Video(BaseVideo):

    def __new__(cls, model_block):
        if model_block.layout == 'zmo-xl-header':
            return
        return super(Video, cls).__new__(cls, model_block)

    def __init__(self, model_block):
        super(Video, self).__init__(model_block)


@grokcore.component.implementer(IFrontendHeaderBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IVideo)
class HeaderVideo(BaseVideo):

    def __new__(cls, model_block):
        if model_block.layout != 'zmo-xl-header':
            return
        return super(HeaderVideo, cls).__new__(cls, model_block)

    def __init__(self, model_block):
        super(HeaderVideo, self).__init__(model_block)


@grokcore.component.implementer(IFrontendBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IGallery)
def inlinegallery(context):
    # Inline galleries are created dynamically via this factory because
    # they inherit from zeit.web.core.gallery.Gallery. Declaring a regular
    # class would introduce a circular dependency.
    from zeit.web.core.gallery import Gallery
    cls = type('Inlinegallery', (Gallery,), {})
    return cls(context.references)


@grokcore.component.implementer(IFrontendBlock)
@grokcore.component.adapter(zeit.newsletter.interfaces.IGroup)
class NewsletterGroup(object):

    type = 'group'

    def __init__(self, context):
        self.context = context
        self.title = context.title

    def values(self):
        return [IFrontendBlock(x) for x in self.context.values()]


@grokcore.component.implementer(IFrontendBlock)
@grokcore.component.adapter(zeit.newsletter.interfaces.ITeaser)
class NewsletterTeaser(object):

    autoplay = None

    def __init__(self, context):
        self.context = context
        if zeit.content.video.interfaces.IVideoContent.providedBy(
                context.reference):
            self.more = 'Video starten'
            self.autoplay = True
        else:
            self.more = 'weiterlesen'

    @property
    def image(self):
        if zeit.content.video.interfaces.IVideoContent.providedBy(
                self.context.reference):
            return self.context.reference.thumbnail
        images = zeit.content.image.interfaces.IImages(
            self.context.reference, None)
        group = images.image if images is not None else None
        if group is None:
            return
        # XXX An actual API for selecting a size would be nice.
        for name in group:
            basename, ext = os.path.splitext(name)
            if basename.endswith('148x84'):
                image = group[name]
                return image.uniqueId.replace(
                    'http://xml.zeit.de/', 'http://images.zeit.de/', 1)

    @property
    def videos(self):
        body = zeit.content.article.edit.interfaces.IEditableBody(
            self.context.reference)
        return [IFrontendBlock(element)
                for element in body.values()
                if zeit.content.article.edit.interfaces.IVideo.providedBy(
                    element)]

    @property
    def url(self):
        url = self.uniqueId.replace(
            'http://xml.zeit.de/', 'http://www.zeit.de/', 1)
        if self.autoplay:
            url += '#autoplay'
        return url

    def __getattr__(self, name):
        return getattr(self.context.reference, name)


@grokcore.component.implementer(IFrontendBlock)
@grokcore.component.adapter(zeit.newsletter.interfaces.IAdvertisement)
class NewsletterAdvertisement(object):

    type = 'advertisement'

    def __init__(self, context):
        self.context = context
        self.title = context.title
        self.text = context.text
        self.url = context.href

    @property
    def image(self):
        return self.context.image.uniqueId.replace(
            'http://xml.zeit.de/', 'http://images.zeit.de/', 1)


def _raw_html(xml):
    filter_xslt = lxml.etree.XML("""
        <xsl:stylesheet version="1.0"
            xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
            <xsl:output method="html"
                        omit-xml-declaration="yes" />
          <xsl:template match="raw">
            <xsl:copy-of select="*" />
          </xsl:template>
        </xsl:stylesheet>
    """)
    transform = lxml.etree.XSLT(filter_xslt)
    return transform(xml)


def _inline_html(xml):
    allowed_elements = 'a|span|strong|img|em|sup|sub|caption|br'
    filter_xslt = lxml.etree.XML("""
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
        </xsl:stylesheet>""" % (allowed_elements))
    try:
        transform = lxml.etree.XSLT(filter_xslt)
        return transform(xml)
    except TypeError:
        return


class NextreadLayout(object):

    """Implementation to match layout sources from centerpages."""

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.image_pattern = 'zmo-nextread'

    def __eq__(self, value):
        return self.id == value

    def __ne__(self, value):
        return self.id != value


@grokcore.component.implementer(zeit.web.core.interfaces.INextreadTeaserBlock)
@grokcore.component.adapter(zeit.content.article.interfaces.IArticle)
class NextreadTeaserBlock(object):

    """Teaser block for nextread teasers in articles."""

    def __init__(self, context):
        self.teasers = zeit.magazin.interfaces.INextRead(
            context).nextread

        # Select layout id from a list of possible values, default to 'base'.
        layout_id = (
            lambda l: l if l in ('base', 'minimal', 'maximal') else 'base')(
            zeit.magazin.interfaces.IRelatedLayout(context).nextread_layout)
        self.layout = NextreadLayout(id=layout_id)
        # TODO: Nextread lead should be configurable with ZMO-185.
        self.lead = 'Lesen Sie jetzt:'
        self.multitude = 'multi' if len(self) - 1 else 'single'

    def __iter__(self):
        return iter(self.teasers)

    def __getitem__(self, index):
        return self.teasers[index]

    def __len__(self):
        return len(self.teasers)
