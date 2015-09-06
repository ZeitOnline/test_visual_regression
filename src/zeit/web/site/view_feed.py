import calendar
import datetime
import email
import logging
import urllib

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
ELEMENT_MAKER = lxml.objectify.ElementMaker(annotate=False, nsmap={
    'atom': ATOM_NAMESPACE, 'content': CONTENT_NAMESPACE})
ATOM_MAKER = getattr(ELEMENT_MAKER, '{%s}link' % ATOM_NAMESPACE)
CONTENT_MAKER = getattr(ELEMENT_MAKER, '{%s}encoded' % CONTENT_NAMESPACE)


def format_rfc822_date(date):
    if date is None:
        date = datetime.datetime.min
    return email.utils.formatdate(calendar.timegm(date.timetuple()))


def last_published_semantic(context):
    return zeit.cms.workflow.interfaces.IPublishInfo(
        context).date_last_published_semantic


@pyramid.view.view_config(
    context=zeit.content.cp.interfaces.ICenterPage,
    route_name='newsfeed',
    renderer='string')
class Newsfeed(zeit.web.core.view.Base):

    def __call__(self):
        super(Newsfeed, self).__call__()
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
        for content in zeit.content.cp.interfaces.ITeaseredContent(
                self.context):
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
        for content in zeit.content.cp.interfaces.ICPFeed(self.context).items:
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
