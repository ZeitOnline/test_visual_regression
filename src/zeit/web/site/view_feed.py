#!/usr/bin/env python
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

@pyramid.view.view_defaults(
    context=zeit.content.cp.interfaces.ICP2015,
    renderer='string')
@pyramid.view.view_config(
    route_name='newsfeed')
@pyramid.view.view_config(
    header='host:newsfeed.zeit.de',
    custom_predicates=(zeit.web.site.view.is_zon_content,))
@pyramid.view.view_config(
    header='host:newsfeed.zeit.de',
    custom_predicates=(zeit.web.magazin.view.is_zmo_content,))
class Newsfeed(zeit.web.core.view.Base):

    def __call__(self):
        super(Newsfeed, self).__call__()
        self.request.response.content_type = 'application/rss+xml'
        return lxml.etree.tostring(
            self.build_feed(), pretty_print=True, xml_declaration=True,
            encoding='UTF-8')

    def build_feed(self):
        year = datetime.datetime.today().year
        root = ELEMENT_MAKER.rss(version='2.0')
        channel = ELEMENT_MAKER.channel(
            ELEMENT_MAKER.title(self.pagetitle),
            ELEMENT_MAKER.link(self.request.route_url('home')),
            ELEMENT_MAKER.description(self.pagedescription),
            ELEMENT_MAKER.language('de-de'),
            ELEMENT_MAKER.copyright(
                u'Copyright © {}, ZEIT ONLINE GmbH'.format(year)),
            ATOM_MAKER(href=self.request.url,
                       type=self.request.response.content_type),
            ELEMENT_MAKER.docs('http://www.zeit.de/hilfe/rss'),
            ELEMENT_MAKER.generator('zeit.web {}'.format(
                self.request.registry.settings.version)),
            ELEMENT_MAKER.managingEditor(
                'online-cr.zeit.de (Chefredaktion ZEIT ONLINE)'),
            ELEMENT_MAKER.webMaster('webmaster@zeit.de (Technik ZEIT ONLINE)'),
            ELEMENT_MAKER.image(
                ELEMENT_MAKER.url(('http://images.zeit.de/bilder/elemente_01_'
                                   '06/logos/homepage_top.gif')),
                ELEMENT_MAKER.title(self.pagetitle),
                ELEMENT_MAKER.link(self.request.route_url('home'))
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

            teaser_image = zeit.web.core.template.get_variant(
                zeit.content.image.interfaces.IImages(content).image, 'wide')

            description = content.teaserText
            if teaser_image:
                description = (u'<a href="{}"><img style="float:left; '
                               'margin-right:5px" src="{}"></a> {}').format(
                                    content_url,
                                    '{}{}__148x84'.format(
                                        self.request.asset_url('/'),
                                        teaser_image.path),
                                    content.teaserText)

            item = ELEMENT_MAKER.item(
                ELEMENT_MAKER.title(content.title),
                ELEMENT_MAKER.link(content_url),
                ELEMENT_MAKER.description(description),
                ELEMENT_MAKER.category(content.sub_ressort or content.ressort),
                DC_MAKER(u'ZEIT ONLINE: {} - {}'.format(
                    (content.sub_ressort or content.ressort),
                    u', '.join(authors))),
                ELEMENT_MAKER.pubDate(format_rfc822_date(
                    last_published_semantic(content))),
                ELEMENT_MAKER.guid(content_url, isPermaLink='false'),
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
        root = ELEMENT_MAKER.rss(version='2.0')
        channel = ELEMENT_MAKER.channel(
            ELEMENT_MAKER.title('Spektrum Kooperationsfeed'),
            ELEMENT_MAKER.link(self.request.route_url('home')),
            ELEMENT_MAKER.description(),
            ELEMENT_MAKER.language('de-de'),
            ELEMENT_MAKER.copyright(
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
            item = ELEMENT_MAKER.item(
                ELEMENT_MAKER.title(content.title),
                ELEMENT_MAKER.link('%s?%s' % (content_url, tracking)),
                ELEMENT_MAKER.description(content.teaserText),
                ELEMENT_MAKER.pubDate(format_rfc822_date(
                    last_published_semantic(content))),
                ELEMENT_MAKER.guid(content.uniqueId, isPermaLink='false'),
            )
            image = zeit.content.image.interfaces.IMasterImage(
                zeit.content.image.interfaces.IImages(content).image, None)
            if image is not None:
                image_url = zeit.web.core.template.default_image_url(
                    image, 'spektrum')
                image_url = image_url.replace(
                    self.request.route_url('home'),
                    self.request.asset_url('/'), 1)
                item.append(ELEMENT_MAKER.enclosure(
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
        root = ELEMENT_MAKER.rss(version='2.0')
        channel = ELEMENT_MAKER.channel(
            ELEMENT_MAKER.title('ZEIT ONLINE SocialFlow'),
            ELEMENT_MAKER.link(self.request.route_url('home')),
            ELEMENT_MAKER.description(),
            ELEMENT_MAKER.language('de-de'),
            ELEMENT_MAKER.copyright(
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
            item = ELEMENT_MAKER.item(
                ELEMENT_MAKER.title(content.title),
                ELEMENT_MAKER.link(content_url),
                ELEMENT_MAKER.description(content.teaserText),
                ELEMENT_MAKER.pubDate(
                    format_rfc822_date(last_published_semantic(content))),
                ELEMENT_MAKER.guid(content.uniqueId, isPermaLink='false'),
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
