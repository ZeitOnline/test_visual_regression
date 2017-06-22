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
        return url.replace('http://newsfeed', 'http://www', 1)
    else:
        return url


def join_queries(url, join_query):
    scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
    query = urllib.urlencode(urlparse.parse_qsl(query) + join_query)
    return urlparse.urlunparse([scheme, netloc, path, params, query, fragment])


@zeit.web.view_defaults(renderer='string')
class Base(zeit.web.core.view.Base):

    @property
    def items(self):
        return zeit.content.cp.interfaces.ITeaseredContent(self.context)

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


@zeit.web.view_config(
    context=zeit.content.cp.interfaces.ICP2015,
    host_restriction='newsfeed')
class Newsfeed(Base):

    def __call__(self):
        # Make newsfeed cachingtime configurable.
        zope.interface.alsoProvides(
            self.context, zeit.web.core.interfaces.INewsfeed)
        super(Newsfeed, self).__call__()
        self.request.response.content_type = 'application/rss+xml'
        return lxml.etree.tostring(
            self.build_feed(), pretty_print=True, xml_declaration=True,
            encoding='UTF-8')

    def build_feed(self):
        E = ELEMENT_MAKER
        EN = ELEMENT_NS_MAKER
        year = datetime.datetime.today().year
        root = E.rss(version='2.0')
        channel = E.channel(
            E.title(self.pagetitle),
            E.link('http://www.zeit.de%s' % self.request.path),
            E.description(self.pagedescription),
            E.language('de-de'),
            E.copyright(
                u'Copyright © {}, ZEIT ONLINE GmbH'.format(year)),
            EN('atom', 'link',
               href=self.request.url.decode('utf-8'),
               type=self.request.response.content_type),
            E.docs('http://www.zeit.de/hilfe/rss'),
            E.generator('zeit.web {}'.format(
                self.request.registry.settings.version)),
            E.managingEditor(
                'online-cr@zeit.de (Chefredaktion ZEIT ONLINE)'),
            E.webMaster('webmaster@zeit.de (Technik ZEIT ONLINE)'),
            E.image(
                E.url((self.request.image_host +
                       '/bilder/elemente_01_06/logos/homepage_top.gif')),
                E.title(self.pagetitle),
                E.link('http://www.zeit.de%s' % self.request.path)
            )
        )
        root.append(channel)

        for content in filter_and_sort_entries(self.items)[:15]:
            try:
                metadata = zeit.cms.content.interfaces.ICommonMetadata(
                    content, None)
                if metadata is None:
                    continue

                content_url = zeit.web.core.template.create_url(
                    None, content, self.request)
                content_url = create_public_url(content_url)

                description = metadata.teaserText

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
                            metadata.teaserText)

                item = E.item(
                    E.title(self.make_title(metadata)),
                    E.link(content_url),
                    E.description(description),
                    E.category(metadata.sub_ressort or metadata.ressort),
                    EN('dc', 'creator', u'ZEIT ONLINE: {} - {}'.format(
                        (metadata.sub_ressort or metadata.ressort),
                        u', '.join(self.make_author_list(metadata)))),
                    E.pubDate(format_rfc822_date(
                        last_published_semantic(content))),
                    E.guid(content_url, isPermaLink='false'),
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
        return zeit.content.cp.interfaces.ITeaseredContent(
            zeit.web.site.view_author.create_author_article_area(
                self.context, count=8, dedupe_favourite_content=False))


@zeit.web.view_config(
    context=zeit.content.cp.interfaces.ICenterPage,
    name='rss-instantarticle',
    host_restriction='newsfeed')
class InstantArticleFeed(Newsfeed):

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
        root = E.rss(version='2.0')
        channel = E.channel(
            E.title(self.pagetitle),
            E.link(self.request.route_url('home')),
            E.description(self.pagedescription),
            E.language('de-de'),
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

    def __call__(self):
        super(SpektrumFeed, self).__call__()
        self.request.response.content_type = 'application/rss+xml'
        return lxml.etree.tostring(
            self.build_feed(), pretty_print=True, xml_declaration=True,
            encoding='UTF-8')

    def build_feed(self):
        E = ELEMENT_MAKER
        EN = ELEMENT_NS_MAKER
        root = E.rss(version='2.0')
        channel = E.channel(
            E.title('Spektrum Kooperationsfeed'),
            E.link(self.request.route_url('home')),
            E.description(),
            E.language('de-de'),
            E.copyright(
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
                item = E.item(
                    E.title(content.title),
                    E.link(link),
                    E.description(content.teaserText),
                    E.pubDate(format_rfc822_date(
                        last_published_semantic(content))),
                    E.guid(content.uniqueId, isPermaLink='false'),
                )
                image = zeit.web.core.template.get_image(content,
                                                         fallback=False)
                if image:
                    item.append(E.enclosure(
                        url='{}{}__180x120'.format(
                            self.request.image_host, image.path),
                        length='10240',  # ¯\_(ツ)_/¯
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

    def __call__(self):
        super(SocialFeed, self).__call__()
        self.request.response.content_type = 'application/rss+xml'
        return lxml.etree.tostring(
            self.build_feed(), pretty_print=True, xml_declaration=True,
            encoding='UTF-8')

    def build_feed(self):
        E = ELEMENT_MAKER
        EN = ELEMENT_NS_MAKER
        root = E.rss(version='2.0')
        channel = E.channel(
            E.title('ZEIT ONLINE SocialFlow'),
            E.link(self.request.route_url('home')),
            E.description(),
            E.language('de-de'),
            E.copyright(
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
                item = E.item(
                    E.title(self.make_title(content)),
                    E.link(content_url),
                    E.description(content.teaserText),
                    E.pubDate(
                        format_rfc822_date(last_published_semantic(content))),
                    E.guid(content.uniqueId, isPermaLink='false'),
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
class YahooFeed(SocialFeed):

    def __call__(self):
        if self.context.uniqueId != 'http://xml.zeit.de/'\
                'administratives/yahoofeed':
            raise pyramid.httpexceptions.HTTPNotFound()

        return super(YahooFeed, self).__call__()

    def build_feed(self):
        E = ELEMENT_MAKER
        EN = ELEMENT_NS_MAKER
        root = E.rss(version='2.0')
        channel = E.channel(
            E.title('ZEIT ONLINE Newsfeed for Yahoo'),
            E.link(self.request.route_url('home')),
            E.description(),
            E.language('de-de'),
            E.copyright(
                'Copyright ZEIT ONLINE GmbH. Alle Rechte vorbehalten'),
            E.generator('zeit.web {}'.format(
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

                item = E.item(
                    E.title(self.make_title(content)),
                    E.link(content_url),
                    E.description(content.teaserText or content.subtitle),
                    E.pubDate(format_rfc822_date(
                        last_published_semantic(content))),
                    E.guid(content.uniqueId, isPermaLink='false'),
                    E.category(content.ressort)
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
class MsnFeed(SocialFeed):

    def __call__(self):
        if self.context.uniqueId != 'http://xml.zeit.de/'\
                'administratives/msnfeed':
            raise pyramid.httpexceptions.HTTPNotFound()

        return super(MsnFeed, self).__call__()

    def make_image_url(self, image, image_width):
        image_height = int(image_width / image.ratio)
        # XXX: remove as soon as we have SSL
        image_host = self.request.image_host.replace(
            'http://', 'https://')
        image_url = '{}{}__{}x{}__desktop'.format(
            image_host, image.path, image_width, image_height)
        return image_url

    def get_image_item(self, content):
        EN = ELEMENT_NS_MAKER
        image = zeit.web.core.template.get_image(
            content, variant_id='wide', fallback=False)
        if image:
            image_url = self.make_image_url(image, 1200)
            imageitem = EN(
                'media', 'content', url=image_url, type='image/jpeg')
            imageitem.append(EN('mi', 'hasSyndicationRights', '0'))
            imageitem.append(EN('media', 'title', image.caption))
            imageitem.append(EN('media', 'text', image.caption))
            imageitem.append(EN('media', 'thumbnail',
                                url=image_url, type='image/jpeg'))

            if image.copyrights:
                copyright_names = []
                for name, url, nofollow in image.copyrights:
                    copyright_names.append(name)
                copyright_names_string = ', '.join(copyright_names)

                imageitem.append(EN(
                    'mi', 'licensorName', copyright_names_string))
                imageitem.append(EN(
                    'mi', 'credit', copyright_names_string))

            return imageitem

    def get_related_item(self, content):
        E = ELEMENT_MAKER
        EN = ELEMENT_NS_MAKER

        nextread = zeit.web.core.interfaces.INextread(content, [])
        if nextread:

            related_url = nextread.uniqueId
            related_title = self.make_title(nextread)[0:150]

            relateditem = E('link', type='text/html',
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
        root = E.rss(version='2.0')
        channel = E.channel(
            E.title('ZEIT ONLINE Newsfeed for MSN'),
            E.link(self.request.route_url('home')),
            E.description(),
            E.language('de-de'),
            E.copyright(
                'Copyright ZEIT ONLINE GmbH. Alle Rechte vorbehalten'),
            E.generator('zeit.web {}'.format(
                self.request.registry.settings.version)),
            EN('atom', 'link',
               href=self.request.url, type=self.request.response.content_type)
        )
        root.append(channel)

        for index, content in enumerate(self.items):
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

                item = E.item(
                    E.title(item_title),
                    E.webUrl(content_url),
                    E.abstract(content.teaserText or content.subtitle),
                    E.publishedDate(item_published_date),
                    E.guid(content_url),
                    E.publisher('ZEIT Online')
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

                imageitem = self.get_image_item(content)
                if imageitem is not None:
                    item.append(imageitem)

                relateditem = self.get_related_item(content)
                if relateditem is not None:
                    item.append(relateditem)

                channel.append(item)
            except:
                log.warning(
                    'Error adding %s to %s',
                    content, self.__class__.__name__, exc_info=True)
                continue

        lxml.etree.cleanup_namespaces(root)
        return root
