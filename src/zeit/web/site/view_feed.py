# -*- coding: utf-8 -*-

import calendar
import datetime
import email
import logging
import urllib
import pytz

import pyramid.view
import lxml.etree
import lxml.objectify

import zeit.content.cp.interfaces
import zeit.cms.interfaces
import zeit.push.interfaces

import zeit.web.core.interfaces
import zeit.web.core.template
import zeit.web.core.view_centerpage
import zeit.web.site.view


log = logging.getLogger(__name__)


ATOM_NAMESPACE = 'http://www.w3.org/2005/Atom'
CONTENT_NAMESPACE = 'http://purl.org/rss/1.0/modules/content/'
DC_NAMESPACE = 'http://purl.org/dc/elements/1.1/'
ELEMENT_MAKER = lxml.objectify.ElementMaker(annotate=False, nsmap={
    'atom': ATOM_NAMESPACE, 'content': CONTENT_NAMESPACE, 'dc': DC_NAMESPACE})
ATOM_MAKER = getattr(ELEMENT_MAKER, '{%s}link' % ATOM_NAMESPACE)
CONTENT_MAKER = getattr(ELEMENT_MAKER, '{%s}encoded' % CONTENT_NAMESPACE)
DC_MAKER = getattr(ELEMENT_MAKER, '{%s}creator' % DC_NAMESPACE)


def format_rfc822_date(date):
    if date is None:
        date = datetime.datetime.min
    return email.utils.formatdate(calendar.timegm(date.timetuple()))


def last_published_semantic(context):
    return zeit.cms.workflow.interfaces.IPublishInfo(
        context).date_last_published_semantic


def lps_sort(context):
    return zeit.cms.workflow.interfaces.IPublishInfo(
        context).date_last_published_semantic or datetime.datetime(
            datetime.MINYEAR, 1, 1, tzinfo=pytz.UTC)


class Base(zeit.web.core.view.Base):
    pass


@pyramid.view.view_defaults(
    context=zeit.content.cp.interfaces.ICP2015,
    renderer='string')
@pyramid.view.view_config(
    route_name='newsfeed')
@pyramid.view.view_config(
    header='host:newsfeed(\.staging)?\.zeit\.de',
    custom_predicates=(zeit.web.site.view.is_zon_content,))
class Newsfeed(Base):

    def __call__(self):
        super(Newsfeed, self).__call__()
        self.request.response.content_type = 'application/rss+xml'
        return lxml.etree.tostring(
            self.build_feed(), pretty_print=True, xml_declaration=True,
            encoding='UTF-8')

    def build_feed(self):
        E = ELEMENT_MAKER
        year = datetime.datetime.today().year
        root = E.rss(version='2.0')
        channel = E.channel(
            E.title(self.pagetitle),
            E.link(self.request.route_url('home')),
            E.description(self.pagedescription),
            E.language('de-de'),
            E.copyright(
                u'Copyright © {}, ZEIT ONLINE GmbH'.format(year)),
            ATOM_MAKER(href=self.request.url,
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
                E.link(self.request.route_url('home'))
                )
            )
        root.append(channel)
        filter_news = filter(lambda c: '/news' not in c.uniqueId,
                             zeit.content.cp.interfaces.ITeaseredContent(
                                 self.context))
        entries = sorted(filter_news, key=lps_sort, reverse=True)

        for content in entries[1:15]:
            content_url = zeit.web.core.template.create_url(
                None, content, self.request)
            # XXX Since this view will be accessed via newsfeed.zeit.de, we
            # cannot use route_url() as is, since it uses that hostname, which
            # is not the one we want. In non-production environments this
            # unfortunately still generates useless production links.
            content_url = content_url.replace(
                self.request.route_url('home'), 'http://www.zeit.de/', 1)

            authors = [getattr(author.target, 'display_name') for author in (
                content.authorships)] if getattr(
                    content, 'authorships') else []

            description = content.teaserText
            teaser_image = zeit.content.image.interfaces.IImages(content).image
            variant = teaser_image.variant_url('wide', 148, 84) if (
                teaser_image) else None

            if variant:
                description = (u'<a href="{}"><img style="float:left; '
                               'margin-right:5px" src="{}"></a> {}').format(
                                    content_url,
                                    '{}{}'.format(
                                        self.request.asset_url('/'),
                                        variant.lstrip('/')),
                                    content.teaserText)

            item = E.item(
                E.title(content.title),
                E.link(content_url),
                E.description(description),
                E.category(content.sub_ressort or content.ressort),
                DC_MAKER(u'ZEIT ONLINE: {} - {}'.format(
                    (content.sub_ressort or content.ressort),
                    u', '.join(authors))),
                E.pubDate(format_rfc822_date(
                    last_published_semantic(content))),
                E.guid(content_url, isPermaLink='false'),
            )
            channel.append(item)
        return root


@pyramid.view.view_config(
    context=zeit.content.cp.interfaces.ICenterPage,
    name='rss-spektrum-flavoured',
    renderer='string')
class SpektrumFeed(zeit.web.site.view.Base):

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
        filter_news = filter(lambda c: '/news' not in c.uniqueId,
                             zeit.content.cp.interfaces.ITeaseredContent(
                                 self.context))
        entries = sorted(filter_news, key=lps_sort, reverse=True)
        for content in entries[1:100]:
            normalized_title = zeit.cms.interfaces.normalize_filename(
                content.title)
            tracking = urllib.urlencode({
                'wt_zmc':
                'koop.ext.zonaudev.spektrumde.feed.%s.bildtext.link.x' % (
                    normalized_title),
                'utm_medium': 'koop',
                'utm_source': 'spektrumde_zonaudev_ext',
                'utm_campaign': 'feed',
                'utm_content': '%s_bildtext_link_x' % normalized_title,
            })
            content_url = zeit.web.core.template.create_url(
                None, content, self.request)
            # XXX Since this view will be accessed via newsfeed.zeit.de, we
            # cannot use route_url() as is, since it uses that hostname, which
            # is not the one we want. In non-production environments this
            # unfortunately still generates useless production links.
            content_url = content_url.replace(
                self.request.route_url('home'), 'http://www.zeit.de/', 1)
            item = E.item(
                E.title(content.title),
                E.link('%s?%s' % (content_url, tracking)),
                E.description(content.teaserText),
                E.pubDate(format_rfc822_date(
                    last_published_semantic(content))),
                E.guid(content.uniqueId, isPermaLink='false'),
            )
            image = zeit.content.image.interfaces.IMasterImage(
                zeit.content.image.interfaces.IImages(content).image, None)
            if image is not None:
                image_url = zeit.web.core.template.default_image_url(
                    image, 'spektrum')
                image_url = image_url.replace(
                    self.request.route_url('home'),
                    self.request.asset_url('/'), 1)
                item.append(E.enclosure(
                    url=image_url,
                    # XXX Incorrect length, since bitblt will resize the image,
                    # but since that happens outside of the application, we
                    # cannot know the real size here.
                    length=str(image.size),
                    type=image.mimeType))
            channel.append(item)
        return root


# XXX This is a copy&paste&tweak of the above SpektrumFeed.
# Could we extract common functionality somehow?
class SocialFeed(zeit.web.site.view.Base):

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
        # We want all teasers available in the cp, not just the limited amount
        # available in the ICPFeed.
        for content in zeit.content.cp.interfaces.ITeaseredContent(
                self.context):
            content_url = zeit.web.core.template.create_url(
                None, content, self.request)
            # XXX Since this view will be accessed via newsfeed.zeit.de, we
            # cannot use route_url() as is, since it uses that hostname, which
            # is not the one we want. In non-production environments this
            # unfortunately still generates un-unseful production links.
            content_url = content_url.replace(
                self.request.route_url('home'), 'http://www.zeit.de/', 1)
            item = E.item(
                E.title(content.title),
                E.link(content_url),
                E.description(content.teaserText),
                E.pubDate(
                    format_rfc822_date(last_published_semantic(content))),
                E.guid(content.uniqueId, isPermaLink='false'),
            )
            social_value = getattr(
                zeit.push.interfaces.IPushMessages(content), self.social_field)
            if social_value:
                item.append(CONTENT_MAKER(social_value))
            channel.append(item)
        return root


@pyramid.view.view_config(
    context=zeit.content.cp.interfaces.ICenterPage,
    name='rss-socialflow-twitter',
    renderer='string')
class TwitterFeed(SocialFeed):

    social_field = 'short_text'


@pyramid.view.view_config(
    context=zeit.content.cp.interfaces.ICenterPage,
    name='rss-socialflow-facebook',
    renderer='string')
class FacebookFeed(SocialFeed):

    social_field = 'long_text'
