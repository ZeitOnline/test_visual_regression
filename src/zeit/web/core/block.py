# -*- coding: utf-8 -*-
import datetime
import logging
import os.path

import babel.dates
import beaker.cache
import grokcore.component
import lxml.etree
import lxml.html
import pyramid
import requests
import requests.exceptions
import urlparse
import zope.component
import zope.interface

import zeit.content.article.edit.body
import zeit.content.article.edit.interfaces
import zeit.content.image.interfaces
import zeit.content.video.interfaces
import zeit.magazin.interfaces
import zeit.newsletter.interfaces

import zeit.web
import zeit.web.core.interfaces


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IParagraph)
class Paragraph(object):

    def __init__(self, model_block):
        self.html = _inline_html(model_block.xml)

    def __str__(self):
        return unicode(self.html)


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
@grokcore.component.adapter(
    zeit.content.article.edit.interfaces.IUnorderedList)
class UnorderedList(Paragraph):

    def __init__(self, model_block):
        # Vivi does not allow nested lists, so we don't care about that for now
        additional_elements = ['li']
        self.html = _inline_html(model_block.xml, additional_elements)


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IOrderedList)
class OrderedList(UnorderedList):
    pass


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IPortraitbox)
class Portraitbox(object):

    def __init__(self, model_block):
        if model_block.references is not None:
            self.text = self._author_text(model_block.references.text)
            self.name = model_block.references.name

    def _author_text(self, pbox):
        # not the most elegant solution, but it gets sh*t done
        return ''.join([lxml.etree.tostring(element) for element in
                       lxml.html.fragments_fromstring(pbox) if
                       element.tag != 'raw'])


class IInfoboxDivision(zope.interface.Interface):
    pass


@grokcore.component.implementer(
    zeit.content.article.edit.interfaces.IEditableBody)
@grokcore.component.adapter(IInfoboxDivision)
class InfoboxDivision(zeit.content.article.edit.body.EditableBody):

    def values(self):
        result = []
        for child in self.xml.iterchildren():
            element = self._get_element_for_node(child)
            if element is None:
                element = self._get_element_for_node(
                    child, zeit.edit.block.UnknownBlock.type)
            result.append(element)
        return result


@grokcore.component.adapter(InfoboxDivision)
@grokcore.component.implementer(zeit.content.article.interfaces.IArticle)
def make_article_blocks_work_with_infobox_content(context):
    return context.__parent__


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IInfobox)
class Infobox(object):

    def __init__(self, model_block):
        self.contents = []
        if model_block.references is None:
            return
        try:
            self.title = model_block.references.supertitle
        except:
            self.title = 'infobox'
        for block in model_block.references.xml.xpath('block'):
            text = block.find('text')
            title = block.find('title')
            division = InfoboxDivision(model_block.references, text)
            self.contents.append(
                (title, [zeit.web.core.interfaces.IFrontendBlock(
                    b, None) for b in division.values()]))


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.ILiveblog)
class Liveblog(object):

    timeout = 1

    def __init__(self, model_block):
        self.blog_id = model_block.blog_id
        self.is_live = False
        self.last_modified = None
        self.id = None
        self.seo_id = None

        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        self.status_url = conf.get('liveblog_status_url')

        try:
            self.id, self.seo_id = self.blog_id.split('-')[:2]
        except ValueError:
            self.id = self.blog_id

        url = '{}/Blog/{}/Post/Published'
        content = self.get_restful(url.format(self.status_url, self.id))

        if (content and 'PostList' in content and len(
                content['PostList']) and 'href' in content['PostList'][0]):
            href = content['PostList'][0]['href']
            content = self.get_restful(self.prepare_ref(href))
            if content:
                tz = babel.dates.get_timezone('Europe/Berlin')
                utc = babel.dates.get_timezone('UTC')
                date_format = '%d.%m.%y %H:%M'
                if '/' in content['PublishedOn']:
                    date_format = '%m/%d/%y %I:%M %p'
                elif '-' in content['PublishedOn']:
                    date_format = '%Y-%m-%dT%H:%M:%SZ'
                self.last_modified = datetime.datetime.strptime(
                    content['PublishedOn'], date_format).replace(
                        tzinfo=utc).astimezone(tz)
                delta = self.last_modified - datetime.datetime.now(
                    self.last_modified.tzinfo)
                if delta.days == 0:
                    self.is_live = True

        # only needed for beta testing with liveblog embed code
        # ToDo: remove after finished relaunch
        self.theme = self.get_theme(self.id)

    def prepare_ref(self, url):
        return 'http:{}'.format(url).replace(
            'http://zeit.superdesk.pro/resources/LiveDesk', self.status_url, 1)

    def get_restful(self, url):
        try:
            return requests.get(url, timeout=self.timeout).json()
        except (requests.exceptions.RequestException, ValueError):
            pass

    @beaker.cache.cache_region('long_term', 'liveblog_theme')
    def get_theme(self, blog_id):
        href = None
        blog_theme_id = None

        if self.seo_id is None:
            url = '{}/Blog/{}/Seo'
            content = self.get_restful(url.format(self.status_url, self.id))
            if (content and 'SeoList' in content and len(
                    content['SeoList']) and 'href' in content['SeoList'][0]):
                href = content['SeoList'][0]['href']
        else:
            href = '//zeit.superdesk.pro/resources/LiveDesk/Seo/{}'.format(
                self.seo_id)

        if href:
            content = self.get_restful(self.prepare_ref(href))
            if content and 'BlogTheme' in content:
                try:
                    blog_theme_id = int(content['BlogTheme']['Id'])
                except (KeyError, ValueError):
                    pass

        # return new theme names
        # 23 = zeit      => zeit-online
        # 24 = zeit-solo => zeit-online-solo
        if blog_theme_id == 24:
            return 'zeit-online-solo'

        return 'zeit-online'


class BaseImage(object):

    @property
    def ratio(self):
        try:
            width, height = self.image.getImageSize()
            return float(width) / float(height)
        except (TypeError, ZeroDivisionError):
            return

    def getImageSize(self):  # NOQA
        try:
            return self.image.getImageSize()
        except AttributeError:
            return


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
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
            bu_node = model_block.xml.find('bu')
            bu = unicode(_inline_html(bu_node) or '').strip()
            if bu:
                # Repair encoded entities
                bu = lxml.html.fromstring(bu).text_content().strip()

            self.align = model_block.xml.get('align')
            self.href = model_block.xml.get('href')
            self.caption = bu
            self.attr_title = bu
            self.attr_alt = bu
            cr = model_block.xml.find('copyright')
            if cr is not None:
                rel = cr.attrib.get('rel', '') == 'nofollow'
                self.copyright = ((cr.text, cr.attrib.get('link', None), rel),)

        # XXX: This is a rather unelegant and inflexible!
        #      But it gets images rolling in beta articles - so wth.
        #      … and 99% of images in articles are 'large'
        target = model_block.references and model_block.references.target
        if zeit.content.image.interfaces.IImageGroup.providedBy(target):
            try:
                target = target['wide']
            except KeyError:
                target = None

        if target:
            self.image = target
            self.src = self.image and self.image.uniqueId
            self.uniqueId = self.image and self.image.uniqueId
            if model_block.references.title:
                self.attr_title = model_block.references.title
            if model_block.references.alt:
                self.attr_alt = model_block.references.alt
        else:
            self.image = None
            self.src = None


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendHeaderBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IImage)
class HeaderImage(Image):

    def __new__(cls, model_block):
        if (model_block.layout != 'zmo-xl-header' or
                getattr(model_block, 'is_empty', False)):
            return
        return super(Image, cls).__new__(cls, model_block)

    def __init__(self, model_block):
        super(HeaderImage, self).__init__(model_block)


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendHeaderBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IImage)
class HeaderImageStandard(HeaderImage):
    pass


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IIntertitle)
class Intertitle(object):

    def __init__(self, model_block):
        self.text = unicode(model_block.text)

    def __str__(self):
        return self.text


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IRawXML)
class Raw(object):

    def __init__(self, model_block):
        self.alldevices = 'alldevices' in model_block.xml.keys()
        self.xml = _raw_html(model_block.xml)


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
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
        if self.renditions:
            high = sorted(self.renditions, key=lambda r: r.frame_width).pop()
            return getattr(high, 'url', '')
        else:
            logging.exception('No video renditions set.')


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IVideo)
class Video(BaseVideo):

    def __new__(cls, model_block):
        if model_block.layout == 'zmo-xl-header':
            return
        return super(Video, cls).__new__(cls, model_block)

    def __init__(self, model_block):
        super(Video, self).__init__(model_block)


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendHeaderBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IVideo)
class HeaderVideo(BaseVideo):

    def __new__(cls, model_block):
        if model_block.layout != 'zmo-xl-header':
            return
        return super(HeaderVideo, cls).__new__(cls, model_block)

    def __init__(self, model_block):
        super(HeaderVideo, self).__init__(model_block)


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IGallery)
def inlinegallery(context):
    # Inline galleries are created dynamically via this factory because
    # they inherit from zeit.web.core.gallery.Gallery. Declaring a regular
    # class would introduce a circular dependency.
    from zeit.web.core.gallery import Gallery
    cls = type('Inlinegallery', (Gallery,), {})
    if context.references is None:
        return None
    return cls(context.references)


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
@grokcore.component.adapter(zeit.newsletter.interfaces.IGroup)
class NewsletterGroup(object):

    type = 'group'

    def __init__(self, context):
        self.context = context
        self.title = context.title

    def values(self):
        return [zeit.web.core.interfaces.IFrontendBlock(x)
                for x in self.context.values()]


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
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
    def imagegroup(self):
        if zeit.content.video.interfaces.IVideoContent.providedBy(
                self.context.reference):
            return self.context.reference.thumbnail
        images = zeit.content.image.interfaces.IImages(
            self.context.reference, None)
        return images.image if images is not None else None

    @property
    def image(self):
        # XXX An actual API for selecting a size would be nice.
        if self.imagegroup is None:
            return
        for name in self.imagegroup:
            basename, ext = os.path.splitext(name)
            if basename.endswith('148x84'):
                image = self.imagegroup[name]
                return image.uniqueId.replace(
                    'http://xml.zeit.de/', 'http://images.zeit.de/', 1)

    @property
    def videos(self):
        body = zeit.content.article.edit.interfaces.IEditableBody(
            self.context.reference, None)
        if body is None:
            return []
        return [zeit.web.core.interfaces.IFrontendBlock(element)
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


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
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


def _inline_html(xml, elements=None):

    home_url = "http://www.zeit.de/"

    try:
        request = pyramid.threadlocal.get_current_request()
        home_url = request.route_url('home')
    except:
        pass

    allowed_elements = 'a|span|strong|img|em|sup|sub|caption|br|entity'
    if elements:
        elements.append(allowed_elements)
        allowed_elements = '|'.join(elements)
    filter_xslt = lxml.etree.XML("""
        <xsl:stylesheet version="1.0"
            xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
            <xsl:output method="html"
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
          <xsl:template match="entity">
                <a>
                    <xsl:attribute name="href">
                        <xsl:value-of select="concat(
                            '%sthema/',
                            substring-after(@url_value, '/'))" />
                    </xsl:attribute>
                    <xsl:apply-templates />
                </a>
          </xsl:template>
        </xsl:stylesheet>""" % (allowed_elements, home_url))
    try:
        transform = lxml.etree.XSLT(filter_xslt)
        return transform(xml)
    except TypeError:
        return


class Nextread(zeit.web.core.utils.nslist):
    """Teaser block for nextread teasers in articles."""

    image_pattern = 'default'

    def __init__(self, context, *args):
        super(Nextread, self).__init__(*args)
        self.context = context

    @property
    def teasers(self):
        raise NotImplementedError()

    @zeit.web.reify
    def layout_id(self):
        # Select layout id from a list of possible values, default to 'base'.
        related = zeit.magazin.interfaces.IRelatedLayout(self.context)
        layout = related.nextread_layout
        return layout if layout in ('minimal', 'maximal') else 'base'

    @zeit.web.reify
    def layout(self):
        return zeit.content.cp.layout.BlockLayout(
            self.layout_id, self.layout_id,
            areas=[], image_pattern=self.image_pattern)

    @zeit.web.reify
    def multitude(self):
        return 'multi' if len(self) > 1 else 'single'

    def __hash__(self):
        return hash(self.context.uniqueId)

    def __repr__(self):
        return object.__repr__(self)


@grokcore.component.implementer(zeit.web.core.interfaces.INextread)
@grokcore.component.adapter(zeit.magazin.interfaces.IZMOContent)
class ZMONextread(Nextread):

    image_pattern = 'zmo-nextread'

    def __init__(self, context):
        nxr = zeit.magazin.interfaces.INextRead(context, None)
        args = nxr.nextread if nxr and nxr.nextread else ()
        super(ZMONextread, self).__init__(context, args)


@grokcore.component.implementer(zeit.web.core.interfaces.INextread)
@grokcore.component.adapter(zeit.cms.interfaces.ICMSContent)
class ZONNextread(Nextread):

    image_pattern = '940x400'

    def __init__(self, context):
        rel = zeit.cms.related.interfaces.IRelatedContent(context, None)
        args = rel.related if rel and rel.related else ()
        super(ZONNextread, self).__init__(context, args)


@grokcore.component.implementer(zeit.web.core.interfaces.IBreakingNews)
@grokcore.component.adapter(zeit.content.article.interfaces.IArticle)
class BreakingNews(object):

    def __init__(self):
        bn_path = zope.component.getUtility(
            zeit.web.core.interfaces.ISettings).get('breaking_news_config')
        try:
            bn_banner_content = zeit.cms.interfaces.ICMSContent(bn_path)
        except TypeError:
            self.published = False
            return
        self.published = zeit.cms.workflow.interfaces.IPublishInfo(
            bn_banner_content).published
        bn_banner = zeit.content.article.edit.interfaces.IBreakingNewsBody(
            bn_banner_content)
        self.uniqueId = bn_banner.article_id
        bn_article = zeit.cms.interfaces.ICMSContent(self.uniqueId)
        bd_date = zeit.cms.workflow.interfaces.IPublishInfo(
            bn_article).date_first_released
        if bd_date:
            tz = babel.dates.get_timezone('Europe/Berlin')
            bd_date = bd_date.astimezone(tz)
        self.title = bn_article.title
        self.date_first_released = bd_date
        self.doc_path = urlparse.urlparse(bn_article.uniqueId).path
