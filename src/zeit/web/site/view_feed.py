# -*- coding: utf-8 -*-

import calendar
import datetime
import email
import logging
import pytz
import types
import urllib
import urlparse

import pyramid.view
import lxml.builder
import lxml.etree

import zeit.content.cp.interfaces
import zeit.content.image.interfaces
import zeit.cms.interfaces
import zeit.push.interfaces

import zeit.web
import zeit.web.core.cachingtime
import zeit.web.core.template
import zeit.web.site.view


log = logging.getLogger(__name__)

ATOM_NAMESPACE = 'http://www.w3.org/2005/Atom'
CONTENT_NAMESPACE = 'http://purl.org/rss/1.0/modules/content/'
DC_NAMESPACE = 'http://purl.org/dc/elements/1.1/'
ESI_NAMESPACE = 'http://www.edge-delivery.org/esi/1.0'
ELEMENT_MAKER = lxml.builder.ElementMaker(nsmap={
    'atom': ATOM_NAMESPACE, 'content': CONTENT_NAMESPACE, 'dc': DC_NAMESPACE,
    'esi': ESI_NAMESPACE},
    typemap={types.NoneType: lambda elem, txt: setattr(elem, 'text', ''),
             lxml.etree.CDATA: lambda elem, txt: setattr(elem, 'text', txt)})
ATOM_MAKER = getattr(ELEMENT_MAKER, '{%s}link' % ATOM_NAMESPACE)
CONTENT_MAKER = getattr(ELEMENT_MAKER, '{%s}encoded' % CONTENT_NAMESPACE)
DC_MAKER = getattr(ELEMENT_MAKER, '{%s}creator' % DC_NAMESPACE)


def format_rfc822_date(date):
    if date is None:
        date = datetime.datetime.min
    return email.utils.formatdate(calendar.timegm(date.timetuple()))


def format_iso8601_date(date):
    if date is None:
        date = datetime.datetime.min
    return date.isoformat()


def last_published_semantic(context):
    return zeit.cms.workflow.interfaces.IPublishInfo(
        context).date_last_published_semantic


DATE_MIN = datetime.datetime(datetime.MINYEAR, 1, 1, tzinfo=pytz.UTC)


def lps_sort(context):
    info = zeit.cms.workflow.interfaces.IPublishInfo(context, None)
    if info is None:
        return DATE_MIN
    return info.date_last_published_semantic or DATE_MIN


def filter_and_sort_entries(items):
    filter_news = filter(
        lambda c: '/news' not in c.uniqueId,
        items)
    return sorted(filter_news, key=lps_sort, reverse=True)


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


class Base(zeit.web.core.view.Base):

    allowed_on_hosts = ['newsfeed']

    @property
    def items(self):
        return zeit.content.cp.interfaces.ITeaseredContent(self.context)


@pyramid.view.view_defaults(
    context=zeit.content.cp.interfaces.ICP2015,
    renderer='string')
@pyramid.view.view_config(
    header='host:newsfeed(\.staging)?\.zeit\.de',
    # We need to be as specific as the normal views with `is_zon_content` etc.
    custom_predicates=(lambda *_: True,))
class Newsfeed(Base):

    def __call__(self):
        super(Newsfeed, self).__call__()
        self.request.response.content_type = 'application/rss+xml'
        self.request.response.cache_expires(
            zeit.web.core.cachingtime.caching_time_feed(self.context))
        return lxml.etree.tostring(
            self.build_feed(), pretty_print=True, xml_declaration=True,
            encoding='UTF-8')

    def build_feed(self):
        E = ELEMENT_MAKER
        year = datetime.datetime.today().year
        root = E.rss(version='2.0')
        channel = E.channel(
            E.title(self.pagetitle),
            E.link('http://www.zeit.de%s' % self.request.path),
            E.description(self.pagedescription),
            E.language('de-de'),
            E.copyright(
                u'Copyright © {}, ZEIT ONLINE GmbH'.format(year)),
            ATOM_MAKER(href=self.request.url.decode('utf-8'),
                       type=self.request.response.content_type),
            E.docs('http://www.zeit.de/hilfe/rss'),
            E.generator('zeit.web {}'.format(
                self.request.registry.settings.version)),
            E.managingEditor(
                'online-cr.zeit.de (Chefredaktion ZEIT ONLINE)'),
            E.webMaster('webmaster@zeit.de (Technik ZEIT ONLINE)'),
            E.image(
                E.url(('http://images.zeit.de/bilder/elemente_01_'
                       '06/logos/homepage_top.gif')),
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

                authors = []
                if getattr(content, 'authorships', None):
                    for author in content.authorships:
                        name = getattr(author.target, 'display_name', None)
                        if name:
                            authors.append(name)

                description = metadata.teaserText

                title = ': '.join(t for t in (
                    metadata.supertitle, metadata.title) if t)

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
                    E.title(title),
                    E.link(content_url),
                    E.description(description),
                    E.category(metadata.sub_ressort or metadata.ressort),
                    DC_MAKER(u'ZEIT ONLINE: {} - {}'.format(
                        (metadata.sub_ressort or metadata.ressort),
                        u', '.join(authors))),
                    E.pubDate(format_rfc822_date(
                        last_published_semantic(content))),
                    E.guid(content_url, isPermaLink='false'),
                )
                channel.append(item)
            except:
                pass
        return root


@pyramid.view.view_config(
    route_name='newsfeed')
@pyramid.view.view_config(
    header='host:newsfeed(\.staging)?\.zeit\.de',
    context='zeit.content.author.interfaces.IAuthor')
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


@pyramid.view.view_defaults(
    context=zeit.content.cp.interfaces.ICenterPage,
    renderer='string')
@pyramid.view.view_config(
    header='host:newsfeed(\.staging)?\.zeit\.de',
    name='rss-instantarticle')
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

            content_url = create_public_url(
                zeit.web.core.template.create_url(
                    None, content, self.request))

            scheme, netloc, path, _, _, _ = urlparse.urlparse(content_url)
            instant_articles_url = (
                '{}://{}/instantarticle-item{}'.format(
                    scheme, netloc, path))

            include = getattr(E, '{%s}include' % ESI_NAMESPACE)(
                src=instant_articles_url, onerror='continue')
            channel.append(include)

        return root


@pyramid.view.view_config(
    context=zeit.content.cp.interfaces.ICenterPage,
    name='rss-spektrum-flavoured',
    renderer='string')
class SpektrumFeed(Base):

    def __call__(self):
        super(SpektrumFeed, self).__call__()
        self.request.response.content_type = 'application/rss+xml'
        return lxml.etree.tostring(
            self.build_feed(), pretty_print=True, xml_declaration=True,
            encoding='UTF-8')

    def build_feed(self):
        E = ELEMENT_MAKER
        root = E.rss(version='2.0')
        channel = E.channel(
            E.title('Spektrum Kooperationsfeed'),
            E.link(self.request.route_url('home')),
            E.description(),
            E.language('de-de'),
            E.copyright(
                'Copyright ZEIT ONLINE GmbH. Alle Rechte vorbehalten'),
            ATOM_MAKER(href=self.request.url,
                       type=self.request.response.content_type)
        )
        root.append(channel)
        for content in filter_and_sort_entries(self.items)[1:100]:
            normalized_title = zeit.cms.interfaces.normalize_filename(
                content.title)
            tracking = [
                ('wt_zmc', ('koop.ext.zonaudev.spektrumde.feed.{}.bildtext.'
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
            image = zeit.web.core.template.get_image(content, fallback=False)
            if image:
                variant = image.group['super']
                item.append(E.enclosure(
                    url='{}{}__180x120'.format(
                        self.request.image_host, image.path),
                    length='10240',  # ¯\_(ツ)_/¯
                    type=variant.mimeType))
            channel.append(item)
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
        root = E.rss(version='2.0')
        channel = E.channel(
            E.title('ZEIT ONLINE SocialFlow'),
            E.link(self.request.route_url('home')),
            E.description(),
            E.language('de-de'),
            E.copyright(
                'Copyright ZEIT ONLINE GmbH. Alle Rechte vorbehalten'),
            ATOM_MAKER(href=self.request.url,
                       type=self.request.response.content_type)
        )
        root.append(channel)

        for content in self.items:
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
                item.append(CONTENT_MAKER(social_value))
            channel.append(item)
        return root

    def make_title(self, content):
        if content.supertitle:
            return u'{}: {}'.format(content.supertitle, content.title)
        else:
            return content.title


@pyramid.view.view_config(
    context=zeit.content.cp.interfaces.ICenterPage,
    name='rss-socialflow-twitter',
    renderer='string')
class TwitterFeed(SocialFeed):

    def social_value(self, content):
        return zeit.push.interfaces.IPushMessages(content).short_text


@pyramid.view.view_config(
    context=zeit.content.cp.interfaces.ICenterPage,
    name='rss-socialflow-facebook',
    renderer='string')
class FacebookFeed(SocialFeed):

    def social_value(self, content):
        return zeit.push.interfaces.IAccountData(content).facebook_main_text


@pyramid.view.view_config(
    context=zeit.content.cp.interfaces.ICenterPage,
    name='rss-socialflow-facebook-zmo',
    renderer='string')
class FacebookMagazinFeed(SocialFeed):

    def social_value(self, content):
        return zeit.push.interfaces.IAccountData(content).facebook_magazin_text


@pyramid.view.view_config(
    context=zeit.content.cp.interfaces.ICenterPage,
    name='rss-socialflow-facebook-zco',
    renderer='string')
class FacebookCampusFeed(SocialFeed):

    def social_value(self, content):
        return zeit.push.interfaces.IAccountData(content).facebook_campus_text


@pyramid.view.view_config(
    context=zeit.content.cp.interfaces.ICenterPage,
    name='rss-roost',
    renderer='string')
class RoostFeed(SocialFeed):

    def make_title(self, content):
        return content.supertitle

    def social_value(self, content):
        return zeit.push.interfaces.IAccountData(content).mobile_text
