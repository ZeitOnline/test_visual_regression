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
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IAuthor)
class Authorbox(Block):
    def __init__(self, model_block):
        self.author = model_block.references.target
        self.text = model_block.references.biography


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


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IVolume)
class Volume(Block):

    def __init__(self, model_block):
        result = model_block.references
        volume_obj = result.target
        article = zeit.content.article.interfaces.IArticle(model_block)
        self.printcover = volume_obj.get_cover(
            'printcover', article.product.id)
        self.medium = self._product_path(volume_obj.product.id)
        self.year = volume_obj.year
        self.issue = str(volume_obj.volume).zfill(2)
        self.teaser_text = result.teaserText

    def _product_path(self, product_id):
        # TODO add more product-url mappings to the dictionary
        # The path will be used in hyperlinks to premium
        # (https://premium.zeit.de/diezeit/2016/01)
        map_product_path = {'ZEI': 'diezeit'}
        return map_product_path.get(product_id, 'diezeit')


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

        # set last_modified
        url = '{}/Blog/{}/Post/Published'
        content = self.get_restful(url.format(self.status_url, self.id))

        if (content and 'PostList' in content and len(
                content['PostList']) and 'href' in content['PostList'][0]):
            href = content['PostList'][0]['href']
            content = self.get_restful(self.prepare_ref(href))
            if content and 'PublishedOn' in content:
                self.last_modified = self.format_date(content['PublishedOn'])

        # set is_live
        url = '{}/Blog/{}'
        content = self.get_restful(url.format(self.status_url, self.id))

        if content and 'ClosedOn' not in content:
            self.is_live = True

    def format_date(self, date):
        tz = babel.dates.get_timezone('Europe/Berlin')
        utc = babel.dates.get_timezone('UTC')
        date_format = '%d.%m.%y %H:%M'
        if '/' in date:
            date_format = '%m/%d/%y %I:%M %p'
        elif '-' in date:
            date_format = '%Y-%m-%dT%H:%M:%SZ'
        return datetime.datetime.strptime(
            date, date_format).replace(tzinfo=utc).astimezone(tz)

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
class Image(Block):

    def __init__(self, context):
        self.context = context
        self.display_mode = context.display_mode
        self.block_type = 'image'
        self.variant_name = context.variant_name
        try:
            image = zeit.content.image.interfaces.IImages(self).image
            if image.display_type == (
                    zeit.content.image.interfaces.INFOGRAPHIC_DISPLAY_TYPE):
                self.block_type = 'infographic'
                self.variant_name = 'original'
        except:
            pass

        # `legacy_layout` is required for bw compat of the ZCO default variant,
        # which is `portrait` rather the usual `wide`.
        self.legacy_layout = context.xml.get('layout', None)

    FIGURE_MODS = {
        'large': ('wide', 'rimless', 'apart'),
        'column-width': ('apart',),
        'float': ('marginalia',),
    }

    @property
    def figure_mods(self):
        return self.FIGURE_MODS.get(self.display_mode, ())


@grokcore.component.adapter(
    zeit.content.article.edit.interfaces.IImage,
    zeit.content.article.edit.interfaces.IHeaderArea
)
@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
class HeaderImage(Image):

    block_type = 'image'

    def __init__(self, model_block, header):
        super(HeaderImage, self).__init__(model_block)
        # XXX Header images should not use `display_mode` at all, they should
        # depend on article.header_layout instead. But since we mostly reuse
        # the normal image templates for the header image, we pretend a fixed
        # display_mode accordingly.
        self.display_mode = 'large'


@grokcore.component.implementer(zeit.content.image.interfaces.IImages)
@grokcore.component.adapter(Image)
class BlockImages(object):

    fill_color = None

    def __init__(self, context):
        self.context = context
        self.image = None
        if context.context.is_empty:
            return
        reference = zeit.content.image.interfaces.IImageReference(
            context.context.references, None)
        if reference and reference.target:
            self.image = reference.target


@grokcore.component.implementer(zeit.content.image.interfaces.IImages)
@grokcore.component.adapter(zeit.web.core.interfaces.IBlock)
def images_from_block(context):
    return zope.component.getAdapter(
        context.context, zeit.content.image.interfaces.IImages)


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
def RawText(context):  # NOQA
    return context


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.ICitation)
class Citation(Block):

    def __init__(self, model_block):
        self.url = model_block.url
        self.attribution = model_block.attribution
        self.text = model_block.text
        self.layout = model_block.layout


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IVideo)
class Video(Block):

    def __init__(self, model_block):
        self.video = getattr(model_block, 'video', None)
        if not zeit.content.video.interfaces.IVideo.providedBy(self.video):
            return
        self.renditions = self.video.renditions
        self.video_still = self.video.video_still
        self.title = self.video.title
        self.supertitle = self.video.supertitle
        self.description = self.video.subtitle
        self.video_still_copyright = self.video.video_still_copyright
        self.id = self.video.uniqueId.split('/')[-1]  # XXX ugly
        self.format = model_block.layout

    @property
    def highest_rendition(self):
        if self.renditions:
            high = sorted(self.renditions, key=lambda r: r.frame_width).pop()
            return getattr(high, 'url', '')
        else:
            logging.exception('No video renditions set.')


@grokcore.component.adapter(
    zeit.content.article.edit.interfaces.IVideo,
    zeit.content.article.edit.interfaces.IHeaderArea
)
@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
class HeaderVideo(Video):

    block_type = 'video'

    def __init__(self, model_block, header):
        super(HeaderVideo, self).__init__(model_block)


@grokcore.component.implementer(zeit.web.core.interfaces.IFrontendBlock)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IGallery)
class Gallery(Block):

    def __new__(cls, context):
        if context.references is None:
            return None
        return super(Gallery, cls).__new__(cls, context)

    def __init__(self, context):
        self.context = context.references

    def __iter__(self):
        return iter(self._values)

    def __bool__(self):
        return bool(self._values)

    __nonzero__ = __bool__

    @zeit.web.reify
    def _values(self):
        if self.context is None:
            return []
        return list(self.context.values())

    @zeit.web.reify
    def html(self):
        return zeit.wysiwyg.interfaces.IHTMLContent(self.context).html


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
        image = zeit.web.core.template.get_image(
            self.context.reference, variant_id='wide', fallback=False)
        # XXX We should not hardcode the host, but newsletter is rendered on
        # friedbert-preview, which can't use `image_host`. Should we introduce
        # a separate setting?
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        image_host = conf.get('newslettter_image_host', '').strip('/')
        if image:
            return urlparse.urljoin(image_host, image.group.variant_url(
                image.variant_id, 148, 84))

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
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        content_host = conf.get('newsletter_content_host', '').strip('/')
        url = self.uniqueId.replace(
            'http://xml.zeit.de', content_host, 1)
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
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        return self.context.image.uniqueId.replace(
                'http://xml.zeit.de', conf['image_prefix'], 1)


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

    variant_id = 'default'

    def __init__(self, context, *args):
        super(Nextread, self).__init__(*args)
        self.context = context

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
            areas=[], image_pattern=self.variant_id)

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

    variant_id = 'super'

    def __init__(self, context):
        nxr = zeit.magazin.interfaces.INextRead(context, None)
        args = nxr.nextread if nxr and nxr.nextread else ()
        super(ZMONextread, self).__init__(context, args)


@grokcore.component.implementer(zeit.web.core.interfaces.INextread)
@grokcore.component.adapter(zeit.cms.interfaces.ICMSContent)
class ZONNextread(Nextread):

    variant_id = 'cinema'

    def __init__(self, context):
        rel = zeit.cms.related.interfaces.IRelatedContent(context, None)
        args = rel.related if rel and rel.related else ()
        super(ZONNextread, self).__init__(context, args)


@grokcore.component.implementer(zeit.web.core.interfaces.INextread)
@grokcore.component.adapter(
    zeit.cms.interfaces.ICMSContent, name="advertisement")
class AdvertisementNextread(Nextread):

    variant_id = 'cinema'
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
        values = filter(
            zeit.content.advertisement.interfaces.IAdvertisement.providedBy,
            folder.values())
        try:
            return random.choice(values)
        except IndexError:
            return


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
    if not zeit.cms.repository.interfaces.IFolder.providedBy(folder):
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
