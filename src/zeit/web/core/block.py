# -*- coding: utf-8 -*-
import base64
import datetime
import json
import logging
import random
import re
import urlparse

import babel.dates
import dogpile.cache.api
import grokcore.component
import lxml.etree
import lxml.html
import pyramid
import requests
import requests.exceptions
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
import zeit.web.core.interfaces
import zeit.web.core.metrics
import zeit.web.core.template
import zeit.web.core.utils

log = logging.getLogger(__name__)

DEFAULT_TERM_CACHE = zeit.web.core.cache.get_region('default_term')
LONG_TERM_CACHE = zeit.web.core.cache.get_region('long_term')


@zope.interface.implementer(zeit.web.core.interfaces.IArticleModule)
class Module(object):

    def __init__(self, context):
        self.context = context

    def __getattr__(self, name):
        if name == 'layout':
            # `layout` is part of our interface, but we don't want to implement
            # it ourselves, since it is often taken from our context as well.
            return getattr(self.context, name, '')
        else:
            return getattr(self.context, name)

    @zeit.web.reify
    def position(self):
        return self.context.__parent__.index(self.context)


@grokcore.component.implementer(zeit.web.core.interfaces.IArticleModule)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IParagraph)
class Paragraph(Module):

    @zeit.web.reify
    def html(self):
        return _inline_html(self.context.xml)

    def __len__(self):
        try:
            xslt_result = _inline_html(
                self.context.xml, elements=['p', 'initial'])
            text = u''.join(xslt_result.xpath('//text()'))
            return len(text.replace('\n', '').strip())
        except:
            return 0

    def __str__(self):
        return unicode(self.html)

    def __unicode__(self):
        return unicode(self.html)


@grokcore.component.implementer(zeit.web.core.interfaces.IArticleModule)
@grokcore.component.adapter(
    zeit.content.article.edit.interfaces.IUnorderedList)
class UnorderedList(Paragraph):

    @zeit.web.reify
    def html(self):
        # Vivi does not allow nested lists, so we don't care about that for now
        additional_elements = ['li']
        return _inline_html(self.context.xml, additional_elements)


@grokcore.component.implementer(zeit.web.core.interfaces.IArticleModule)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IOrderedList)
class OrderedList(UnorderedList):
    pass


@grokcore.component.implementer(zeit.web.core.interfaces.IArticleModule)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IAuthor)
class Authorbox(Module):

    @zeit.web.reify
    def author(self):
        return self.context.references.target

    @zeit.web.reify
    def text(self):
        return self.context.references.biography


@grokcore.component.implementer(zeit.web.core.interfaces.IArticleModule)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IPortraitbox)
class Portraitbox(Module):

    @zeit.web.reify
    def text(self):
        return self._author_text(getattr(self.context, 'text', None))

    @zeit.web.reify
    def name(self):
        return getattr(self.context, 'name', None)

    def _author_text(self, text):
        if not text:
            return None
        # not the most elegant solution, but it gets sh*t done
        parts = []
        for element in lxml.html.fragments_fromstring(text):
            if isinstance(element, lxml.etree.ElementBase):
                if element.tag == 'raw':
                    continue
                parts.append(lxml.etree.tostring(element))
            else:
                # First item of fragments_fromstring may be str/unicode.
                parts.append(element)
        return ''.join(parts)


@grokcore.component.implementer(zeit.web.core.interfaces.IArticleModule)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IBox)
class Box(Module):
    pass


@grokcore.component.implementer(zeit.content.image.interfaces.IImages)
@grokcore.component.adapter(Box)
def box_images(context):
    return zeit.content.image.interfaces.IImages(context.context)


@grokcore.component.implementer(zeit.web.core.interfaces.IArticleModule)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IVolume)
class Volume(Module):

    def __new__(cls, context):
        if context.references.target is None:
            return None
        return super(Volume, cls).__new__(cls, context)

    def __init__(self, context):
        super(Volume, self).__init__(context)
        result = self.context.references
        volume_obj = result.target
        article = zeit.content.article.interfaces.IArticle(self.context)
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


@grokcore.component.implementer(zeit.web.core.interfaces.IArticleModule)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IInfobox)
class Infobox(Module):

    @zeit.web.reify
    def content(self):
        return self.context.references

    @zeit.web.reify
    def identifier(self):
        try:
            return self.content.uniqueId.split('/')[-1]
        except:
            return 'infobox'

    @zeit.web.reify
    def title(self):
        try:
            return self.content.supertitle
        except:
            return 'infobox'

    @zeit.web.reify
    def contents(self):
        if not zeit.content.infobox.interfaces.IInfobox.providedBy(
                self.content):
            return []
        result = []
        for block in self.content.xml.xpath('block'):
            text = block.find('text')
            title = block.find('title')
            division = InfoboxDivision(self.content, text)
            result.append(
                (title, [zeit.web.core.interfaces.IArticleModule(
                    b, None) for b in division.values()]))
        return result


@grokcore.component.implementer(zeit.web.core.interfaces.IArticleModule)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.ILiveblog)
class Liveblog(Module):

    def __init__(self, context):
        super(Liveblog, self).__init__(context)
        self.blog_id = self.context.blog_id
        self.version = self.context.version
        self.collapse_preceding_content = (
            self.context.collapse_preceding_content)
        self.is_live = False
        self.last_modified = None
        self.id = None
        self.seo_id = None

        if self.version == '3':
            self.set_blog_info()
        else:
            conf = zope.component.getUtility(
                zeit.web.core.interfaces.ISettings)
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
                    self.last_modified = self.format_date(
                        content['PublishedOn'])

            # set is_live
            url = '{}/Blog/{}'
            content = self.get_restful(url.format(self.status_url, self.id))
            if content and 'ClosedOn' not in content:
                self.is_live = True

    def set_blog_info(self):
        json = self.api_blog_request()
        self.is_live = json.get('blog_status') == u'open'
        self.last_modified = self.format_date(json.get('_updated'))

    def _retrieve_auth_token(self):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        url = conf.get('liveblog_api_auth_url_v3')

        username = conf.get('liveblog_api_auth_username_v3')
        password = conf.get('liveblog_api_auth_password_v3')
        headers = {'Content-Type': 'application/json;charset=UTF-8'}
        payload = {'username': username, 'password': password}

        try:
            with zeit.web.core.metrics.http('liveblog3auth') as record:
                response = requests.post(
                    url, data=json.dumps(payload), headers=headers)
                record(response)
            response.raise_for_status()
            return response.json().get('token')
        except requests.exceptions.HTTPError as e:
            log.error(e.message)
        except (requests.exceptions.RequestException, ValueError):
            pass

    def api_blog_request(self, _retries=0):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        api_url = conf.get('liveblog_api_url_v3')
        url = '{}/{}'.format(api_url, self.blog_id)

        if _retries >= 2:
            raise RuntimeError('Maximum retries exceeded for %s' % url)

        token = LONG_TERM_CACHE.get('liveblog_api_auth_token')
        if token is dogpile.cache.api.NO_VALUE:
            token = ''
        headers = {
            'Authorization': 'basic ' + base64.b64encode(token + ':')}

        try:
            with zeit.web.core.metrics.http('liveblog3api') as record:
                response = requests.get(url, headers=headers)
                record(response)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            status = getattr(err.response, 'status_code', 510)
            if status == 401:
                log.debug('Refreshing liveblog3 auth token')
                LONG_TERM_CACHE.set(
                    'liveblog_api_auth_token', self._retrieve_auth_token())
                return self.api_blog_request(_retries=_retries + 1)
            raise
        try:
            return response.json()
        except Exception:
            log.error('%s returned invalid json %r', url, response.text)
            raise ValueError('No valid JSON found for %s' % url)

    def format_date(self, date):
        tz = babel.dates.get_timezone('Europe/Berlin')
        utc = babel.dates.get_timezone('UTC')
        date_format = '%d.%m.%y %H:%M'
        if '/' in date:
            date_format = '%m/%d/%y %I:%M %p'
        elif '+00:00' in date:
            date_format = '%Y-%m-%dT%H:%M:%S+00:00'
        elif '-' in date:
            date_format = '%Y-%m-%dT%H:%M:%SZ'
        return datetime.datetime.strptime(
            date, date_format).replace(tzinfo=utc).astimezone(tz)

    def prepare_ref(self, url):
        return 'http:{}'.format(url).replace(
            'http://zeit.superdesk.pro/resources/LiveDesk', self.status_url, 1)

    def get_restful(self, url):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        response = None
        try:
            with zeit.web.core.metrics.http('liveblog') as record:
                response = requests.get(
                    url, timeout=conf.get('liveblog_timeout', 1))
                record(response)
            return response.json()
        except (requests.exceptions.RequestException, ValueError):
            pass

    @LONG_TERM_CACHE.cache_on_arguments()
    def get_amp_themed_id(self, blog_id):
        if self.version == '3':
            json = self.api_blog_request()
            channels = json.get('public_urls').get('output')
            if channels:
                conf = zope.component.getUtility(
                    zeit.web.core.interfaces.ISettings)
                theme_name = conf.get('liveblog_amp_theme_v3')
                regex = '/([^/]*{}[^/]*/[^/]*)/index.html'.format(theme_name)
                for channel in channels.values():
                    match = re.search(regex, channel)
                    if match is not None:
                        return match.group(1)
        else:
            url = '{}/Blog/{}/Seo'
            content = self.get_restful(url.format(self.status_url, blog_id))

            if content and 'SeoList' in content:
                for item in content['SeoList']:
                    blog_theme_id = None
                    if 'href' in item:
                        seo = self.get_restful(self.prepare_ref(item['href']))
                        if seo and 'BlogTheme' in seo:
                            try:
                                blog_theme_id = int(seo['BlogTheme']['Id'])
                            except (KeyError, ValueError):
                                pass

                            # return SEO ID using AMP theme
                            # 23 = zeit
                            # 24 = zeit-solo
                            # 27 = zeit-amp
                            if blog_theme_id == 27:
                                return '{}-{}'.format(blog_id, seo['Id'])


@grokcore.component.adapter(zeit.content.article.edit.interfaces.IQuiz)
@grokcore.component.implementer(zeit.web.core.interfaces.IArticleModule)
class Quiz(Module):

    @zeit.web.reify
    def url(self):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        return conf.get('quiz_url', '').format(quiz_id=self.context.quiz_id)

    @zeit.web.reify
    def adreload(self):
        return '&adcontrol' if self.context.adreload_enabled else ''


@grokcore.component.implementer(zeit.web.core.interfaces.IArticleModule)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IImage)
class Image(Module):

    def __init__(self, context):
        super(Image, self).__init__(context)
        self.display_mode = context.display_mode
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
@grokcore.component.implementer(zeit.web.core.interfaces.IArticleModule)
class HeaderImage(Image):

    def __init__(self, model_block, header):
        super(HeaderImage, self).__init__(model_block)
        if getattr(self, 'block_type', None) == 'infographic':
            # XXX Annoying special case, header images don't usually use
            # display_mode but rather handle their display in the respective
            # header template, but infographics have their own template that
            # does not distinguish between header and body (at the moment).
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


@grokcore.component.implementer(zeit.web.core.interfaces.IArticleModule)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IIntertitle)
class Intertitle(Module):

    def __str__(self):
        return unicode(self.context.text)


@grokcore.component.implementer(zeit.web.core.interfaces.IArticleModule)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IRawXML)
class Raw(Module):

    @zeit.web.reify
    def alldevices(self):
        return 'alldevices' in self.context.xml.keys()

    @zeit.web.reify
    def xml(self):
        return _raw_html(self.context.xml)


@grokcore.component.implementer(zeit.web.core.interfaces.IArticleModule)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IRawText)
class RawText(Module):
    pass


@grokcore.component.implementer(zeit.web.core.interfaces.IArticleModule)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.ICitation)
class Citation(Module):
    pass


@grokcore.component.implementer(zeit.web.core.interfaces.IArticleModule)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IVideo)
class Video(Module):

    # zeit.web.reify would cause infloop with our getattr.
    @pyramid.decorator.reify
    def video(self):
        video = getattr(self.context, 'video', None)
        if not zeit.content.video.interfaces.IVideo.providedBy(video):
            return None
        return video

    def __getattr__(self, name):
        if self.video is None:
            return None
        return getattr(self.video, name)

    @zeit.web.reify
    def id(self):
        if self.video is None:
            return None
        return self.video.uniqueId.split('/')[-1]  # XXX ugly

    @zeit.web.reify
    def layout(self):
        if self.video is None:
            return None
        return self.context.layout


@grokcore.component.adapter(
    zeit.content.article.edit.interfaces.IVideo,
    zeit.content.article.edit.interfaces.IHeaderArea
)
@grokcore.component.implementer(zeit.web.core.interfaces.IArticleModule)
class HeaderVideo(Video):

    block_type = 'video'

    def __init__(self, context, header):
        super(HeaderVideo, self).__init__(context)


@grokcore.component.implementer(zeit.web.core.interfaces.IArticleModule)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IGallery)
class Gallery(Module):

    def __new__(cls, context):
        if context.references is None:
            return None
        return super(Gallery, cls).__new__(cls, context)

    @zeit.web.reify
    def content(self):
        return self.context.references

    def __iter__(self):
        return iter(self._values)

    def __bool__(self):
        return bool(self._values)

    __nonzero__ = __bool__

    @zeit.web.reify
    def _values(self):
        if self.content is None:
            return []
        return list(self.content.values())

    @zeit.web.reify
    def html(self):
        return zeit.wysiwyg.interfaces.IHTMLContent(self.content).html


@grokcore.component.implementer(zeit.web.core.interfaces.IArticleModule)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IJobTicker)
class JobTicker(Module):

    @zeit.web.reify
    def content(self):
        return self.context.feed

    @zeit.web.reify
    def items(self):
        if not self.content:
            return ()
        return list(zeit.web.site.area.rss.parse_feed(
            self.content.feed_url, 'jobbox_ticker'))

    @zeit.web.reify
    def teaser_text(self):
        return self.content and self.content.teaser

    @zeit.web.reify
    def landing_page_url(self):
        return self.content and self.content.landing_url


@grokcore.component.implementer(zeit.web.core.interfaces.IArticleModule)
@grokcore.component.adapter(zeit.content.article.edit.interfaces.IMail)
class MailForm(Module):

    def __getattr__(self, name):
        return getattr(self.context, name)

    @zeit.web.reify
    def subjects(self):
        source = zeit.content.article.edit.interfaces.IMail['subject'].source
        result = []
        for value in source(self.context):
            result.append(source.factory.getTitle(self.context, value))
        return result


@grokcore.component.adapter(zeit.content.article.edit.interfaces.IPodcast)
@grokcore.component.implementer(zeit.web.core.interfaces.IArticleModule)
class Podcast(Module):

    @zeit.web.reify
    def episode(self):
        podigee = zope.component.getUtility(zeit.web.core.interfaces.IPodigee)
        return podigee.get_episode(self.context.episode_id)

    @zeit.web.reify
    def podcast(self):
        podigee = zope.component.getUtility(zeit.web.core.interfaces.IPodigee)
        return podigee.get_podcast(self.episode['podcast_id'])

    def player_configuration(self, theme):
        # Available themes: zon-standalone, zon-minimal
        url = self.episode.get('permalink')
        if not url:
            return None
        podigee = zope.component.getUtility(zeit.web.core.interfaces.IPodigee)
        config = podigee.get_player_configuration(url)
        if not config:
            return None
        config['options']['theme'] = theme
        return config

    @zeit.web.reify
    def podlove_configuration(self):

        toggles = zeit.web.core.application.FEATURE_TOGGLES
        if not toggles.find('podlove_button'):
            return {}

        # https://github.com/podlove/podlove-subscribe-button#podcast-data-api
        result = {
            'title': self.podcast.get('title'),
            'subtitle': self.podcast.get('subtitle'),
            'description': self.podcast.get('description'),
            'cover': self.podcast.get('cover_image'),
            'external_site_url': self.podcast.get('external_site_url'),
            'podigee_subdomain': self.podcast.get('subdomain'),
            'feeds': [{
                'type': 'audio',
                'format': feed['format'],
                'url': feed['url'],
            } for feed in self.podcast.get('feeds', [])]
        }
        # <https://github.com/podlove/podlove-subscribe-button/blob
        #  /6be9607cf5ce486ff6b28d7df4d6f8a61c14e563/src/coffee/app.coffee#L88>
        if not result['feeds']:
            return {}
        return result


@grokcore.component.adapter(
    zeit.content.article.edit.interfaces.IPodcast,
    zeit.content.article.edit.interfaces.IHeaderArea
)
@grokcore.component.implementer(zeit.web.core.interfaces.IArticleModule)
class HeaderPodcast(Podcast):

    def __init__(self, context, header):
        super(HeaderPodcast, self).__init__(context)


@grokcore.component.implementer(zeit.web.core.interfaces.IArticleModule)
@grokcore.component.adapter(zeit.newsletter.interfaces.IGroup)
class NewsletterGroup(Module):

    type = 'group'

    def values(self):
        return [zeit.web.core.interfaces.IArticleModule(x)
                for x in self.context.values()]


@grokcore.component.implementer(zeit.web.core.interfaces.IArticleModule)
@grokcore.component.adapter(zeit.newsletter.interfaces.ITeaser)
class NewsletterTeaser(Module):

    autoplay = None

    def __init__(self, context):
        super(NewsletterTeaser, self).__init__(context)
        if zeit.content.video.interfaces.IVideoContent.providedBy(
                self.context.reference):
            self.more = 'Video starten'
            self.autoplay = True
        else:
            self.more = 'weiterlesen'

    @property
    def image(self):
        image = zeit.web.core.template.get_image(
            self.context.reference, variant_id='wide', fallback=False)
        # The newsletter is rendered on friedbert-preview, so we cannot use
        # `image_host`, since that would be friedbert-preview itself.
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        image_host = conf.get('newsletter_image_host', '').strip('/')
        if image:
            return urlparse.urljoin(image_host, image.group.variant_url(
                image.variant_id, 148, 84))

    @property
    def videos(self):
        body = zeit.content.article.edit.interfaces.IEditableBody(
            self.context.reference, None)
        if body is None:
            return []
        return [
            zeit.web.core.interfaces.IArticleModule(x) for x in
            body.filter_values(zeit.content.article.edit.interfaces.IVideo)]

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


@grokcore.component.implementer(zeit.web.core.interfaces.IArticleModule)
@grokcore.component.adapter(zeit.newsletter.interfaces.IAdvertisement)
class NewsletterAdvertisement(Module):

    type = 'advertisement'

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
    text = unicode(transform(xml))

    toggles = zeit.web.core.application.FEATURE_TOGGLES
    if toggles.find('https'):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        rewrite_https_links = conf.get(
            'transform_to_secure_links_for', '').split(',')
        for link in rewrite_https_links:
            if link:
                text = text.replace("http://%s" % link, "https://%s" % link)
    return text


def _inline_html(xml, elements=None):

    home_url = "http://www.zeit.de/"
    # Replace 'http' with 'https' for inline links.
    # If all content is migrated, we can delete this code
    additional_xslt = ""
    toggles = zeit.web.core.application.FEATURE_TOGGLES
    if toggles.find('https'):
        ns = lxml.etree.FunctionNamespace(
            'http://namespaces.zeit.de/functions')
        ns['maybe-convert-url'] = (
            lambda x, y: zeit.web.core.utils.maybe_convert_http_to_https(y[0]))
        additional_xslt = """
        <xsl:template match="a/@href">
            <xsl:attribute name="href">
                <xsl:value-of select="f:maybe-convert-url(.)" />
            </xsl:attribute>
        </xsl:template>
        """

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
            xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
            xmlns:f="http://namespaces.zeit.de/functions">
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
          %s
        </xsl:stylesheet>""" % (allowed_elements, home_url, additional_xslt))
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

    @property
    def liveblog(self):
        context = zeit.web.core.template.first_child(self)
        if zeit.web.core.template.liveblog(context):
            return zeit.web.core.interfaces.ILiveblogInfo(context)


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
