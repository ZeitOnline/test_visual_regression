# -*- coding: utf-8 -*-
import datetime
import logging
import random

import babel.dates
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
import zeit.web.core.cache
import zeit.web.core.image
import zeit.web.core.interfaces
import zeit.web.core.metrics


DEFAULT_TERM_CACHE = zeit.web.core.cache.get_region('default_term')


class Block(object):

    layout = ''


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IParagraph)
class Paragraph(Block):

    def __init__(self, model_block):
        self.model_block = model_block
        self.html = _inline_html(model_block.xml)

    def __len__(self):
        try:
            xslt_result = _inline_html(
                self.model_block.xml, elements=['p', 'initial'])
            text = u''.join(xslt_result.xpath('//text()'))
            return len(text.replace('\n', '').strip())
        except:
            return 0

    def __str__(self):
        return unicode(self.html)

    def __unicode__(self):
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
class Portraitbox(Block):

    def __init__(self, model_block):
        pbox = model_block.references
        if zeit.content.portraitbox.interfaces.IPortraitbox.providedBy(pbox):
            self.text = self._author_text(pbox.text)
            self.name = pbox.name

    def _author_text(self, pbox):
        # not the most elegant solution, but it gets sh*t done
        parts = []
        for element in lxml.html.fragments_fromstring(pbox):
            if isinstance(element, lxml.etree.ElementBase):
                if element.tag == 'raw':
                    continue
                parts.append(lxml.etree.tostring(element))
            else:
                # First item of fragments_fromstring may be str/unicode.
                parts.append(element)
        return ''.join(parts)


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
class Infobox(Block):

    def __init__(self, model_block):
        self.context = model_block.references
        self.layout = model_block.layout

    @property
    def identifier(self):
        try:
            return self.context.uniqueId.split('/')[-1]
        except:
            return 'infobox'

    @property
    def title(self):
        try:
            return self.context.supertitle
        except:
            return 'infobox'

    @property
    def contents(self):
        if not zeit.content.infobox.interfaces.IInfobox.providedBy(
                self.context):
            return []
        result = []
        for block in self.context.xml.xpath('block'):
            text = block.find('text')
            title = block.find('title')
            division = InfoboxDivision(self.context, text)
            result.append(
                (title, [zeit.web.core.interfaces.IFrontendBlock(
                    b, None) for b in division.values()]))
        return result


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.ILiveblog)
class Liveblog(Block):

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
                delta = datetime.datetime.now(
                    self.last_modified.tzinfo) - self.last_modified
                # considered live if last post was within given timedelta
                if delta < datetime.timedelta(hours=6):
                    self.is_live = True

    def prepare_ref(self, url):
        return 'http:{}'.format(url).replace(
            'http://zeit.superdesk.pro/resources/LiveDesk', self.status_url, 1)

    def get_restful(self, url):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        try:
            with zeit.web.core.metrics.timer('liveblog.reponse_time'):
                return requests.get(
                    url, timeout=conf.get('liveblog_timeout', 1)).json()
        except (requests.exceptions.RequestException, ValueError):
            pass


@grokcore.component.adapter(zeit.content.article.edit.interfaces.IQuiz)
@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
class Quiz(Block):

    def __init__(self, context):
        self.context = context

    @zeit.web.reify
    def url(self):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        return conf.get('quiz_url', '').format(quiz_id=self.context.quiz_id)

    @zeit.web.reify
    def adreload(self):
        return '&adcontrol' if self.context.adreload_enabled else ''


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IImage)
class Image(zeit.web.core.image.BaseImage):

    DEFAULT_VARIANT = 'wide'

    def __new__(cls, model_block):
        if getattr(model_block, 'is_empty', False):
            return
        # XXX Should we use an actual attribute of ImageLayout instead of
        # a heuristic look at its ID?
        if not cls.wanted_layout(getattr(model_block.layout, 'id', None)):
            return

        target = None
        referenced = None
        try:
            if model_block.references:
                referenced = model_block.references.target
        except TypeError:
            pass  # Unresolveable uniqueId

        if zeit.content.image.interfaces.IImageGroup.providedBy(referenced):
            variant = getattr(model_block.layout, 'variant', None) or (
                cls.DEFAULT_VARIANT)
            try:
                target = referenced[variant]
                group = referenced
            except KeyError:
                target = None
                group = None
        else:
            target = referenced
            group = None

        if zeit.web.core.image.is_image_expired(target):
            target = None

        if not target:
            return

        instance = super(Image, cls).__new__(cls, model_block)
        instance.image = target
        instance.group = group
        instance.src = instance.image.uniqueId
        instance.uniqueId = instance.image.uniqueId
        if model_block.references.title:
            instance.attr_title = model_block.references.title
        if model_block.references.alt:
            instance.attr_alt = model_block.references.alt

        return instance

    @classmethod
    def wanted_layout(cls, layout):
        return 'header' not in (layout or '')

    def __init__(self, model_block):
        self.layout = layout = model_block.layout

        if layout.display_mode == 'large':
            self.figure_mods = ('wide', 'rimless', 'apart')
        elif layout.display_mode == 'float':
            self.figure_mods = ('marginalia',)
        else:
            self.figure_mods = ()

        # TODO: don't use XML but adapt an Image and use it's metadata
        if model_block.xml is not None:
            bu_node = model_block.xml.find('bu')
            bu = unicode(_inline_html(bu_node) or '').strip()
            if bu:
                # Repair encoded entities
                bu = lxml.html.fromstring(bu).text_content().strip()

            self.align = model_block.xml.get('align')
            self.href = model_block.xml.get('href')
            self.caption = self.title = self.alt = bu
            cr = model_block.xml.find('copyright')
            if cr is not None:
                rel = cr.attrib.get('rel', '') == 'nofollow'
                self.copyright = ((cr.text, cr.attrib.get('link', None), rel),)


@grokcore.component.implementer(zeit.content.image.interfaces.IImages)
@grokcore.component.adapter(Image)
class BlockImages(object):

    fill_color = None

    def __init__(self, context):
        self.context = context
        self.image = context.group


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendHeaderBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IImage)
class HeaderImage(Image):

    @classmethod
    def wanted_layout(cls, layout):
        return 'header' in (layout or '')


class HeaderImageStandard(HeaderImage):
    pass


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IIntertitle)
class Intertitle(Block):

    def __init__(self, model_block):
        self.text = unicode(model_block.text)

    def __str__(self):
        return self.text


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IRawXML)
class Raw(Block):

    def __init__(self, model_block):
        self.alldevices = 'alldevices' in model_block.xml.keys()
        self.xml = _raw_html(model_block.xml)


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IRawText)
def RawText(context):
    return context


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.ICitation)
class Citation(Block):

    def __init__(self, model_block):
        self.url = model_block.url
        self.attribution = model_block.attribution
        self.text = model_block.text
        self.layout = model_block.layout


class BaseVideo(Block):

    def __init__(self, model_block):
        video = None
        try:
            video = getattr(model_block, 'video')
        except:
            pass
        if not zeit.content.video.interfaces.IVideo.providedBy(video):
            return
        self.renditions = video.renditions
        self.video_still = video.video_still
        self.title = video.title
        self.supertitle = video.supertitle
        self.description = video.subtitle
        self.id = video.uniqueId.split('/')[-1]  # XXX ugly
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
        if 'header' in (model_block.layout or ''):
            return
        return super(Video, cls).__new__(cls, model_block)

    def __init__(self, model_block):
        super(Video, self).__init__(model_block)


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendHeaderBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IVideo)
class HeaderVideo(BaseVideo):

    def __new__(cls, model_block):
        if 'header' not in (model_block.layout or ''):
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
class NewsletterGroup(Block):

    type = 'group'

    def __init__(self, context):
        self.context = context
        self.title = context.title

    def values(self):
        return [zeit.web.core.interfaces.IFrontendBlock(x)
                for x in self.context.values()]


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
@grokcore.component.adapter(zeit.newsletter.interfaces.ITeaser)
class NewsletterTeaser(Block):

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
        images = zeit.content.image.interfaces.IImages(
            self.context.reference, None)
        image = images.image if images is not None else None
        if not zeit.content.image.interfaces.IImageGroup.providedBy(image):
            return
        if zeit.web.core.image.is_image_expired(image):
            return
        # XXX We should not hardcode the host, but newsletter is rendered on
        # friedbert-preview, which can't use `image_host`. Should we introduce
        # a separate setting?
        return 'http://www.zeit.de' + image.variant_url('wide', 148, 84)

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
class NewsletterAdvertisement(Block):

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


@grokcore.component.implementer(zeit.web.core.interfaces.INextread)
@grokcore.component.adapter(
    zeit.cms.interfaces.ICMSContent, name="advertisement")
class AdvertisementNextread(Nextread):

    image_pattern = '940x400'
    layout_id = 'advertisement'

    def __init__(self, context):
        super(AdvertisementNextread, self).__init__(context)
        metadata = zeit.cms.content.interfaces.ICommonMetadata(context, None)
        if metadata is None:
            return
        nextread = self.random_item(find_nextread_folder(
            metadata.ressort, metadata.sub_ressort))
        if nextread is not None:
            self.append(nextread)

    def random_item(self, folder):
        if not folder:
            return None
        # Invalidate child name cache, since the folder object might have been
        # cached, so its contents may not be up to date.
        folder._local_unique_map_data.clear()
        key = random.sample(folder.keys(), 1)
        if not key:
            return None
        return folder[key[0]]


@DEFAULT_TERM_CACHE.cache_on_arguments()
def find_nextread_folder(ressort, subressort):
    ressort = ressort if ressort else ''
    subressort = subressort if subressort else ''

    folder = zeit.web.core.article.RESSORTFOLDER_SOURCE.find(
        ressort, subressort)
    if not contains_nextreads(folder):
        folder = zeit.web.core.article.RESSORTFOLDER_SOURCE.find(ressort, None)
    if not contains_nextreads(folder):
        return None
    nextread_foldername = zope.component.getUtility(
        zeit.web.core.interfaces.ISettings).get(
            'advertisement_nextread_folder', '')
    return folder[nextread_foldername]


def contains_nextreads(folder):
    if not folder:
        return False
    nextread_foldername = zope.component.getUtility(
        zeit.web.core.interfaces.ISettings).get(
            'advertisement_nextread_folder', '')
    if nextread_foldername not in folder:
        return False
    advertisement_nextread_folder = folder[nextread_foldername]
    return bool(len(advertisement_nextread_folder))


@grokcore.component.implementer(zeit.web.core.interfaces.IBreakingNews)
@grokcore.component.adapter(zeit.content.article.interfaces.IArticle)
class BreakingNews(object):

    def __init__(self):
        bn_path = zope.component.getUtility(
            zeit.web.core.interfaces.ISettings).get('breaking_news_config')
        try:
            bn_banner_content = zeit.cms.interfaces.ICMSContent(bn_path)
        except TypeError:
            bn_banner_content = None
        if not zeit.content.article.interfaces.IArticle.providedBy(
                bn_banner_content):
            self.published = False
            return
        raise RuntimeError('provoked')
        self.published = zeit.cms.workflow.interfaces.IPublishInfo(
            bn_banner_content).published
        bn_banner = zeit.content.article.edit.interfaces.IBreakingNewsBody(
            bn_banner_content)
        self.uniqueId = bn_banner.article_id
        bn_article = zeit.cms.interfaces.ICMSContent(self.uniqueId, None)
        if bn_article is None:
            self.published = False
            return
        bd_date = zeit.cms.workflow.interfaces.IPublishInfo(
            bn_article).date_first_released
        if bd_date:
            tz = babel.dates.get_timezone('Europe/Berlin')
            bd_date = bd_date.astimezone(tz)
        self.title = bn_article.title
        self.date_first_released = bd_date
        self.doc_path = urlparse.urlparse(bn_article.uniqueId).path
