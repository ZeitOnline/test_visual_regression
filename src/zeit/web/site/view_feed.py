# -*- coding: utf-8 -*-
import calendar
import datetime
import email
import logging
import pytz
import types
import urllib
import urlparse
import pyramid

import lxml.builder
import lxml.etree
import zope.interface

import zeit.cms.interfaces
import zeit.content.author.interfaces
import zeit.content.cp.interfaces
import zeit.content.image.interfaces
import zeit.push.interfaces

import zeit.web
import zeit.web.core.interfaces
import zeit.web.core.template

from zeit.web.core.utils import maybe_convert_http_to_https


log = logging.getLogger(__name__)

ELEMENT_MAKER = lxml.builder.ElementMaker(nsmap={
    'atom': 'http://www.w3.org/2005/Atom',
    'content': 'http://purl.org/rss/1.0/modules/content/',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'esi': 'http://www.edge-delivery.org/esi/1.0',
    'mi': 'http://schemas.ingestion.microsoft.com/common/',
    'media': 'http://search.yahoo.com/mrss/'},
    typemap={types.NoneType: lambda elem, txt: setattr(elem, 'text', ''),
             lxml.etree.CDATA: lambda elem, txt: setattr(elem, 'text', txt)})


def ELEMENT_NS_MAKER(namespace, tagname, *args, **kw):
    return getattr(ELEMENT_MAKER, '{%s}%s' % (
        ELEMENT_MAKER._nsmap[namespace], tagname))(*args, **kw)


def format_rfc822_date(date):
    return email.utils.formatdate(calendar.timegm(date.timetuple()))


def format_rfc822_date_gmt(date):
    return email.utils.formatdate(calendar.timegm(
        date.timetuple()), usegmt=True)


def format_iso8601_date(date):
    return date.isoformat()


DATE_MIN = datetime.datetime(datetime.MINYEAR, 1, 1, tzinfo=pytz.UTC)


def last_published_semantic(context):
    info = zeit.cms.workflow.interfaces.IPublishInfo(context, None)
    return getattr(info, 'date_last_published_semantic', None) or DATE_MIN


def first_released(context):
    info = zeit.cms.workflow.interfaces.IPublishInfo(context, None)
    return getattr(info, 'date_first_released', None) or DATE_MIN


def filter_and_sort_entries(items):
    filter_news = filter(
        lambda c: '/news' not in c.uniqueId,
        items)
    return sorted(filter_news, key=last_published_semantic, reverse=True)


def create_public_url(url):
    # Since the feed views will be accessed via newsfeed.zeit.de, we
    # cannot use route_url() as is, since it uses that hostname, which
    # is not the one we want. This is a heuristic attempt that should work
    # in both production and staging (and "localhost" type environments),
    # but at the cost of hard-coding the "newsfeed" hostname here.
    if url.startswith('http://newsfeed'):
        return maybe_convert_http_to_https(
            url.replace('http://newsfeed', 'http://www', 1))
    if url.startswith('https://newsfeed'):
        return url.replace('https://newsfeed', 'https://www', 1)
    else:
        return maybe_convert_http_to_https(url)


def join_queries(url, join_query):
    scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
    query = urllib.urlencode(urlparse.parse_qsl(query) + join_query)
    return urlparse.urlunparse([scheme, netloc, path, params, query, fragment])


def make_guid(content):
    return zeit.cms.content.interfaces.IUUID(content).id


@zeit.web.view_defaults(renderer='string')
class Base(zeit.web.core.view.Base):

    def __call__(self):
        # Make newsfeed cachingtime configurable.
        zope.interface.alsoProvides(
            self.context, zeit.web.core.interfaces.INewsfeed)
        super(Base, self).__call__()
        self.request.response.content_type = 'application/rss+xml'
        feed = self.build_feed()
        lxml.etree.cleanup_namespaces(feed)
        return lxml.etree.tostring(
            feed, pretty_print=True, xml_declaration=True,
            encoding='UTF-8')

    def build_feed(self):
        raise NotImplementedError()

    @property
    def items(self):
        for item in zeit.content.cp.interfaces.ITeaseredContent(self.context):
            metadata = zeit.cms.content.interfaces.ICommonMetadata(item, None)
            if metadata is None:
                log.info('%s ignoring %s, no ICommonMetadata',
                         item, self.__class__.__name__)
                continue
            yield item

    def make_author_list(self, content):
        authors = []
        if getattr(content, 'authorships', None):
            for author in content.authorships:
                name = getattr(author.target, 'display_name', None)
                if name:
                    authors.append(name)
        return authors

    def make_title(self, content):
        if content.supertitle:
            return u'{}: {}'.format(content.supertitle, content.title)
        else:
            return content.title

    def make_content_url(self, content):
        content_url = zeit.web.core.template.create_url(
            None, content, self.request)
        content_url = create_public_url(content_url)
        return content_url

    # This is a bit comlicated. We do want to use immutable guids in our feeds,
    # which do not change if an article URI is changed. But we cannot release
    # that new code suddenly, because that would create new guids for all items
    # in the feed, producing duplicates in the clients. (The RSS reader stored
    # an article yesterday, today it has another guid, so it gets stored
    # again and the user sees two items with the same title and URI, but
    # different guids.)
    #
    # So we define a cutoff-date for old vs new guid creation. And in a few
    # weeks or so (when no old article is shown in our newsfeeds any more) we
    # can remove the code and serve the new guid for all articles in all feeds.
    # Then, every feed can simply use `make_guid`.

    GUID_START = datetime.datetime(2018, 1, 16, tzinfo=pytz.UTC)

    def guid_is_needed(self, content):
        return first_released(content) > self.GUID_START

    def make_guid_or_contenturl(self, content):
        if self.guid_is_needed(content):
            return make_guid(content)
        else:
            return self.make_content_url(content)

    def make_guid_or_contentuid(self, content):
        if self.guid_is_needed(content):
            return make_guid(content)
        else:
            return content.uniqueId


@zeit.web.view_config(
    context=zeit.content.cp.interfaces.ICP2015,
    host_restriction='newsfeed')
class Newsfeed(Base):

    def build_feed(self):
        E = ELEMENT_MAKER
        EN = ELEMENT_NS_MAKER
        year = datetime.datetime.today().year
        root = E('rss', version='2.0')
        channel = E(
            'channel',
            E('title', self.pagetitle),
            E('link', maybe_convert_http_to_https(
                'http://www.zeit.de%s' % self.request.path)),
            E('description', self.pagedescription),
            E('language', 'de-de'),
            E('copyright', u'Copyright © {}, ZEIT ONLINE GmbH'.format(year)),
            EN('atom', 'link',
               href=self.request.url.decode('utf-8'),
               type=self.request.response.content_type),
            E('docs',
              maybe_convert_http_to_https('http://www.zeit.de/hilfe/rss')),
            E('generator', 'zeit.web {}'.format(
                self.request.registry.settings.version)),
            E('managingEditor',
              'online-cr@zeit.de (Chefredaktion ZEIT ONLINE)'),
            E('webMaster', 'webmaster@zeit.de (Technik ZEIT ONLINE)'),
            E(
                'image',
                E('url', (self.request.image_host +
                          '/bilder/elemente_01_06/logos/homepage_top.gif')),
                E('title', self.pagetitle),
                E('link', maybe_convert_http_to_https(
                    'http://www.zeit.de%s' % self.request.path))
            )
        )
        root.append(channel)

        for content in filter_and_sort_entries(self.items)[:15]:
            try:
                content_url = self.make_content_url(content)
                description = content.teaserText

                variant = None
                teaser_image = None
                images = zeit.content.image.interfaces.IImages(content, None)
                if images is not None:
                    teaser_image = images.image
                    # Missing meta files break this, since "Folder has no
                    # attribute variant_url".
                    if zeit.content.image.interfaces.IImageGroup.providedBy(
                            teaser_image):
                        variant = images.image.variant_url('wide', 148, 84)

                if variant and not zeit.web.core.template.expired(
                        teaser_image):
                    description = (
                        u'<a href="{}"><img style="float:left; '
                        'margin-right:5px" src="{}"></a> {}').format(
                        content_url,
                        '{}/{}'.format(
                            self.request.image_host, variant.lstrip('/')),
                        content.teaserText)

                item = E(
                    'item',
                    E('title', self.make_title(content)),
                    E('link', content_url),
                    E('description', description),
                    E('category', content.sub_ressort or content.ressort),
                    EN('dc', 'creator', u'ZEIT ONLINE: {} - {}'.format(
                        (content.sub_ressort or content.ressort),
                        u', '.join(self.make_author_list(content)))),
                    E('pubDate', format_rfc822_date(
                        last_published_semantic(content))),
                    E('guid', self.make_guid_or_contenturl(content),
                        isPermaLink='false'),
                )
                channel.append(item)
            except:
                log.warning(
                    'Error adding %s to %s',
                    content, self.__class__.__name__, exc_info=True)
                continue
        return root


@zeit.web.view_config(
    context=zeit.content.author.interfaces.IAuthor,
    host_restriction='newsfeed')
class AuthorFeed(Newsfeed):

    @zeit.web.reify
    def supertitle(self):
        return u'Autorenfeed {}'.format(self.context.display_name)

    @zeit.web.reify
    def pagedescription(self):
        return u'Alle Artikel von {}'.format(self.context.display_name)

    @zeit.web.reify
    def items(self):
        # XXX Filtering metadata is duplicated from Base.items.
        for item in zeit.content.cp.interfaces.ITeaseredContent(
            zeit.web.site.view_author.create_author_article_area(
                self.context, count=8, dedupe_favourite_content=False)):
            metadata = zeit.cms.content.interfaces.ICommonMetadata(item, None)
            if metadata is None:
                log.warning('%s ignoring %s, no ICommonMetadata',
                            item, self.__class__.__name__)
                continue
            yield item


@zeit.web.view_config(
    context=zeit.content.cp.interfaces.ICenterPage,
    name='rss-instantarticle',
    host_restriction='newsfeed')
class InstantArticleFeed(Base):

    @zeit.web.reify
    def pagetitle(self):
        return u'Instant Article Feed'

    @zeit.web.reify
    def supertitle(self):
        return u'ZEIT ONLINE'

    @zeit.web.reify
    def pagedescription(self):
        return (u'Aktuelle Nachrichten, Kommentare, '
                u'Analysen und Hintergrundberichte aus '
                u'Politik, Wirtschaft, Gesellschaft, Wissen, '
                u'Kultur und Sport lesen Sie auf ZEIT ONLINE.')

    def build_feed(self):
        E = ELEMENT_MAKER
        EN = ELEMENT_NS_MAKER
        build_date = format_iso8601_date(datetime.datetime.today())
        root = E('rss', version='2.0')
        channel = E(
            'channel',
            E('title', self.pagetitle),
            E('link', self.request.route_url('home')),
            E('description', self.pagedescription),
            E('language', 'de-de'),
            build_date
        )
        root.append(channel)

        for content in self.items:
            try:
                content_url = create_public_url(
                    zeit.web.core.template.create_url(
                        None, content, self.request))

                scheme, netloc, path, _, _, _ = urlparse.urlparse(content_url)
                instant_articles_url = (
                    '{}://{}/instantarticle-item{}'.format(
                        scheme, netloc, path))

                channel.append(EN(
                    'esi', 'include',
                    src=instant_articles_url, onerror='continue'))
            except:
                log.warning(
                    'Error adding %s to %s',
                    content, self.__class__.__name__, exc_info=True)
                continue
        return root


@zeit.web.view_config(
    context=zeit.content.cp.interfaces.ICenterPage,
    name='rss-spektrum-flavoured',
    host_restriction='newsfeed')
class SpektrumFeed(Base):

    def build_feed(self):
        E = ELEMENT_MAKER
        EN = ELEMENT_NS_MAKER
        root = E('rss', version='2.0')
        channel = E(
            'channel',
            E('title', 'Spektrum Kooperationsfeed'),
            E('link', self.request.route_url('home')),
            E('description'),
            E('language', 'de-de'),
            E('copyright',
              'Copyright ZEIT ONLINE GmbH. Alle Rechte vorbehalten'),
            EN('atom', 'link',
               href=self.request.url, type=self.request.response.content_type)
        )
        root.append(channel)
        for content in filter_and_sort_entries(self.items)[:100]:
            try:
                normalized_title = zeit.cms.interfaces.normalize_filename(
                    content.title)
                tracking = [
                    ('wt_zmc', ('koop.ext.zonaudev.'
                                'spektrumde.feed.{}.bildtext.'
                                'link.x'.format(normalized_title))),
                    ('utm_medium', 'koop'),
                    ('utm_source', 'spektrumde_zonaudev_ext'),
                    ('utm_campaign', 'feed'),
                    ('utm_content', '%s_bildtext_link_x' % normalized_title),
                ]

                content_url = zeit.web.core.template.create_url(
                    None, content, self.request)
                content_url = create_public_url(content_url)
                link = join_queries(content_url, tracking)
                item = E(
                    'item',
                    E('title', content.title),
                    E('link', link),
                    E('description', content.teaserText),
                    E('pubDate', format_rfc822_date(
                        last_published_semantic(content))),
                    E('guid', self.make_guid_or_contentuid(content),
                        isPermaLink='false'),
                )
                image = zeit.web.core.template.get_image(content,
                                                         fallback=False)
                if image:
                    item.append(E.enclosure(
                        url='{}{}__640x360'.format(
                            self.request.image_host, image.path),
                        length='20480',  # ¯\_(ツ)_/¯
                        type='image/jpeg'))  # ¯\_(ツ)_/¯

                channel.append(item)
            except:
                log.warning(
                    'Error adding %s to %s',
                    content, self.__class__.__name__, exc_info=True)
                continue
        return root


# XXX This is a copy&paste&tweak of the above SpektrumFeed.
# Could we extract common functionality somehow?
class SocialFeed(Base):

    social_field = NotImplemented

    def build_feed(self):
        E = ELEMENT_MAKER
        EN = ELEMENT_NS_MAKER
        root = E('rss', version='2.0')
        channel = E(
            'channel',
            E('title', 'ZEIT ONLINE SocialFlow'),
            E('link', self.request.route_url('home')),
            E('description'),
            E('language', 'de-de'),
            E('copyright',
              'Copyright ZEIT ONLINE GmbH. Alle Rechte vorbehalten'),
            EN('atom', 'link',
               href=self.request.url, type=self.request.response.content_type)
        )
        root.append(channel)

        for content in self.items:
            try:
                content_url = zeit.web.core.template.create_url(
                    None, content, self.request)
                content_url = create_public_url(content_url)
                item = E(
                    'item',
                    E('title', self.make_title(content)),
                    E('link', content_url),
                    E('description', content.teaserText),
                    E('pubDate',
                      format_rfc822_date(last_published_semantic(content))),
                    E('guid', self.make_guid_or_contentuid(content),
                        isPermaLink='false'),
                )
                social_value = self.social_value(content)
                if social_value:
                    item.append(EN('content', 'encoded', social_value))
                channel.append(item)
            except:
                log.warning(
                    'Error adding %s to %s',
                    content, self.__class__.__name__, exc_info=True)
                continue
        return root


@zeit.web.view_config(
    context=zeit.content.cp.interfaces.ICenterPage,
    name='rss-socialflow-twitter',
    host_restriction='newsfeed')
class TwitterFeed(SocialFeed):

    def social_value(self, content):
        return zeit.push.interfaces.IPushMessages(content).short_text


@zeit.web.view_config(
    context=zeit.content.cp.interfaces.ICenterPage,
    name='rss-socialflow-facebook',
    host_restriction='newsfeed')
class FacebookFeed(SocialFeed):

    def social_value(self, content):
        return zeit.push.interfaces.IAccountData(content).facebook_main_text


@zeit.web.view_config(
    context=zeit.content.cp.interfaces.ICenterPage,
    name='rss-socialflow-facebook-zmo',
    host_restriction='newsfeed')
class FacebookMagazinFeed(SocialFeed):

    def social_value(self, content):
        return zeit.push.interfaces.IAccountData(content).facebook_magazin_text


@zeit.web.view_config(
    context=zeit.content.cp.interfaces.ICenterPage,
    name='rss-socialflow-facebook-zco',
    host_restriction='newsfeed')
class FacebookCampusFeed(SocialFeed):

    def social_value(self, content):
        return zeit.push.interfaces.IAccountData(content).facebook_campus_text


@zeit.web.view_config(
    context=zeit.content.cp.interfaces.ICenterPage,
    name='rss-roost',
    host_restriction='newsfeed')
class RoostFeed(SocialFeed):

    def make_title(self, content):
        return content.supertitle

    def social_value(self, content):
        return zeit.push.interfaces.IAccountData(content).mobile_text


@zeit.web.view_config(
    context=zeit.content.cp.interfaces.ICenterPage,
    name='rss-yahoo',
    host_restriction='newsfeed')
class YahooFeed(Base):

    def __call__(self):
        if self.context.uniqueId != 'http://xml.zeit.de/'\
                'administratives/yahoofeed':
            raise pyramid.httpexceptions.HTTPNotFound()

        return super(YahooFeed, self).__call__()

    def build_feed(self):
        E = ELEMENT_MAKER
        EN = ELEMENT_NS_MAKER
        root = E('rss', version='2.0')
        channel = E(
            'channel',
            E('title', 'ZEIT ONLINE Newsfeed for Yahoo'),
            E('link', self.request.route_url('home')),
            E('description'),
            E('language', 'de-de'),
            E('copyright',
              'Copyright ZEIT ONLINE GmbH. Alle Rechte vorbehalten'),
            E('generator', 'zeit.web {}'.format(
                self.request.registry.settings.version)),
            EN('atom', 'link',
               href=self.request.url, type=self.request.response.content_type)
        )
        root.append(channel)

        for index, content in enumerate(self.items):
            try:
                content_url = zeit.web.core.template.create_url(
                    None, content, self.request)
                content_url = create_public_url(content_url)

                item = E(
                    'item',
                    E('title', self.make_title(content)),
                    E('link', content_url),
                    E('description', content.teaserText or content.subtitle),
                    E('pubDate', format_rfc822_date(
                        last_published_semantic(content))),
                    E('guid', self.make_guid_or_contentuid(content),
                        isPermaLink='false'),
                    E('category', content.ressort)
                )

                author = u', '.join(self.make_author_list(content))
                if author:
                    item.append(EN('dc', 'creator', author))

                # This needs _any_ request object. It works even though
                # it is not a request to an article URL
                content_view = zeit.web.site.view_article.YahoofeedArticle(
                    content, self.request)

                content_view.content_url = content_url

                # Yahoofeed provides 8 fulltext articles and 8 "half-page"
                if index > 7:
                    content_view.truncate()

                content_body = pyramid.renderers.render(
                    'zeit.web.site:templates/yahoofeed/item.html', {
                        'view': content_view,
                        'request': self.request
                    })
                item.append(EN('content', 'encoded', content_body))

                channel.append(item)
            except:
                log.warning(
                    'Error adding %s to %s',
                    content, self.__class__.__name__, exc_info=True)
                continue

        return root


@zeit.web.view_config(
    context=zeit.content.cp.interfaces.ICenterPage,
    name='rss-msn',
    host_restriction='newsfeed')
class MsnFeed(Base):

    def __call__(self):
        if self.context.uniqueId != 'http://xml.zeit.de/'\
                'administratives/msnfeed':
            raise pyramid.httpexceptions.HTTPNotFound()

        return super(MsnFeed, self).__call__()

    def make_image_url(self, image, image_width):
        image_height = int(image_width / image.ratio)
        # XXX: remove as soon as we have SSL
        # img.zeit.de is already ssl enabled and can be used here
        # the replacement won't be neccessary, once we have a globally
        # configured SSL.
        image_host = self.request.image_host.replace(
            'http://', 'https://')
        image_url = '{}{}__{}x{}__desktop'.format(
            image_host, image.path, image_width, image_height)
        return image_url

    def get_related_item(self, content):
        E = ELEMENT_MAKER
        EN = ELEMENT_NS_MAKER

        nextread = zeit.web.core.interfaces.INextread(content, [])
        nextread = nextread.context

        metadata = zeit.cms.content.interfaces.ICommonMetadata(
            nextread, None)
        if metadata is None:
            log.warning(
                '%s ignoring nextread %s for %s, no ICommonMetadata',
                nextread, content, self.__class__.__name__)
            return None

        if nextread:
            related_url = nextread.uniqueId
            related_title = self.make_title(metadata)[0:150]

            relateditem = E(
                'link',
                rel='related',
                type='text/html',
                href=related_url,
                title=related_title)

            image = zeit.web.core.template.get_image(
                nextread, variant_id='wide', fallback=False)
            if image:
                image_url = self.make_image_url(image, 600)
                relateditem.append(EN('media', 'thumbnail', url=image_url))
                relateditem.append(EN('media', 'title', image.caption))
                relateditem.append(EN('media', 'text', image.caption))

            return relateditem

    def build_feed(self):
        E = ELEMENT_MAKER
        EN = ELEMENT_NS_MAKER
        root = E('rss', version='2.0')
        channel = E(
            'channel',
            E('title', 'ZEIT ONLINE Newsfeed for MSN'),
            E('link', self.request.route_url('home')),
            E('description'),
            E('language', 'de-de'),
            E(
                'copyright',
                'Copyright ZEIT ONLINE GmbH. Alle Rechte vorbehalten'),
            E('generator', 'zeit.web {}'.format(
                self.request.registry.settings.version)),
            EN('atom', 'link',
               href=self.request.url, type=self.request.response.content_type)
        )
        root.append(channel)

        for content in self.items:
            try:
                content_url = create_public_url(
                    zeit.web.core.template.create_url(
                        None, content, self.request))

                item_title = self.make_title(content)[0:150]

                item_published_date = format_iso8601_date(
                    first_released(content))
                item_written_date = format_iso8601_date(
                    first_released(content))
                item_modified_date = format_iso8601_date(
                    last_published_semantic(content))

                item = E(
                    'item',
                    E('title', item_title),
                    E('webUrl', content_url),
                    E('abstract', content.teaserText or content.subtitle),
                    E('publishedDate', item_published_date),
                    E('guid', self.make_guid_or_contenturl(content),
                        isPermaLink='false'),
                    E('publisher', 'ZEIT Online')
                )

                author = u', '.join(self.make_author_list(content))
                if author:
                    item.append(EN('dc', 'creator', author))

                item.append(EN('dc', 'modified', item_modified_date))
                item.append(EN('mi', 'dateTimeWritten', item_written_date))

                # This needs _any_ request object. It works even though
                # it is not a request to an article URL
                content_view = zeit.web.site.view_article.Article(
                    content, self.request)
                content_body = pyramid.renderers.render(
                    'zeit.web.site:templates/msnfeed/item.html', {
                        'view': content_view,
                        'request': self.request
                    })
                item.append(EN('content', 'encoded', content_body))

                try:
                    relateditem = self.get_related_item(content)
                    if relateditem is not None:
                        item.append(relateditem)
                except:
                    log.warning(
                        'Error adding related on %s at %s',
                        content, self.__class__.__name__, exc_info=True)

                channel.append(item)
            except:
                log.warning(
                    'Error adding %s to %s',
                    content, self.__class__.__name__, exc_info=True)
                continue

        return root


@zeit.web.view_config(
    context=zeit.content.cp.interfaces.ICenterPage,
    name='rss-google-editors-picks',
    host_restriction='newsfeed')
class GoogleEditorsPicksFeed(Base):

    def __call__(self):
        if self.context.uniqueId != 'http://xml.zeit.de/'\
                'administratives/google-editors-picks-feed':
            raise pyramid.httpexceptions.HTTPNotFound()

        return super(GoogleEditorsPicksFeed, self).__call__()

    @property
    def items(self):
        reach = zope.component.getUtility(zeit.web.core.interfaces.IReach)
        # fetch 10, in case some get sorted out later (wrong series/product)
        articles = reach.get_views(section=None, limit=10)

        for item in articles:
            metadata = zeit.cms.content.interfaces.ICommonMetadata(item, None)
            if metadata is None:
                log.info('%s ignoring %s, no ICommonMetadata',
                         item, self.__class__.__name__)
                continue
            yield item

    def build_feed(self):
        homepage_link = maybe_convert_http_to_https(
            'http://www.zeit.de/index')
        feed_title = 'ZEIT ONLINE Newsfeed for Google Editors Picks'
        # the logo file must meet certain conditions
        # https://support.google.com/news/publisher/answer/1407682?hl=en
        publisher_logo = maybe_convert_http_to_https(
            'http://www.zeit.de/static/latest/images/'
            'google-editors-picks-logo-zon.png')
        build_date = format_rfc822_date_gmt(datetime.datetime.today())

        e = ELEMENT_MAKER
        en = ELEMENT_NS_MAKER
        root = e('rss', version='2.0')

        channel = e(
            'channel',
            e('title', feed_title),
            e('link', homepage_link),
            e('description',
                u'Selection of original content for Googles “Editor’s Picks”'),
            e('language', 'de'),
            e('copyright',
              'Copyright ZEIT ONLINE GmbH. Alle Rechte vorbehalten'),
            e('generator', 'zeit.web {}'.format(
                self.request.registry.settings.version)),
            e('lastBuildDate', build_date),
            e(
                'image',
                e('url', publisher_logo),
                e('title', feed_title),  # must match the channel title
                e('link', homepage_link)
            ),
            en(
                'atom',
                'link',
                rel='self',
                href=self.request.url.decode('utf-8'),
                type=self.request.response.content_type
            )
        )
        root.append(channel)

        for index, content in enumerate(self.items):

            try:
                prod = content.product.id
                if prod != 'ZEI' and prod != 'ZEDE':
                    continue

                content_url = zeit.web.core.template.create_url(
                    None, content, self.request)
                content_url = create_public_url(content_url)

                item = e(
                    'item',
                    e('title', self.make_title(content)),
                    e('link', content_url),
                    e('description', content.teaserText or content.subtitle),
                    e('pubDate', format_rfc822_date_gmt(
                        first_released(content))),
                    e('guid', self.make_guid_or_contentuid(content),
                        isPermaLink='false'),
                    e('category', content.ressort)
                )

                author = u', '.join(self.make_author_list(content))
                if not author:
                    author = 'ZEIT ONLINE Redaktion'
                if author:
                    item.append(en('dc', 'creator', author))

                channel.append(item)

                if len(channel.findall('item')) >= 5:
                    break
            except:
                log.warning(
                    'Error adding %s to %s',
                    content, self.__class__.__name__, exc_info=True)
                continue

        return root
