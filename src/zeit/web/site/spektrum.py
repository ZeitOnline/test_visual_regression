# -*- coding: utf-8 -*-

from datetime import datetime
import email.utils
import time

import zope.component
import pyramid.view
import requests
import lxml.etree
import lxml.objectify

import zeit.content.cp.interfaces

import zeit.web.core.interfaces
import zeit.web.core.template
import zeit.web.core.view_centerpage
import zeit.web.site.view


class HPFeed(list):

    def __init__(self):
        """Generate a list of teasers from an RSS feed."""
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        feed_url = conf.get('spektrum_hp_feed')

        try:
            resp = requests.get(feed_url, timeout=2.0)
            xml = lxml.etree.fromstring(resp.content)
            super(HPFeed, self).__init__(
                Teaser(i) for i in xml.xpath('/rss/channel/item'))
        except (requests.exceptions.RequestException,
                lxml.etree.XMLSyntaxError):
            super(HPFeed, self).__init__()


class Teaser(object):

    _map = {'title': 'teaserTitle',
            'description': 'teaserText',
            'link': 'url',
            'guid': 'guid'}

    def __init__(self, item):
        for value in self._map.values():
            setattr(self, value, '')

        self.feed_image = None
        self.teaserSupertitle = ''

        for value in item:
            if value.tag in self._map.keys() and value.text:
                setattr(self, self._map[value.tag], value.text.strip())
            elif value.tag == 'enclosure' and 'url' in value.keys():
                self.feed_image = value.get('url')

        self.teaserSupertitle, self.teaserTitle = self._split(self.teaserTitle)

    def _split(self, title):
        if ':' in title:
            return (title[:title.find(':')].strip(),
                    title[title.find(':') + 1:].strip())
        return ('', title)

    @property
    def image(self):
        try:
            return zeit.web.core.interfaces.ITeaserImage(self)
        except TypeError:
            return


ATOM_NAMESPACE = 'http://www.w3.org/2005/Atom'
ElementMaker = lxml.objectify.ElementMaker(
    annotate=False, nsmap={'atom': ATOM_NAMESPACE})


@pyramid.view.view_config(
    context=zeit.content.cp.interfaces.ICenterPage,
    name='rss-spektrum-flavoured',
    renderer='string')
class RSSFeed(
        zeit.web.core.view_centerpage.Centerpage, zeit.web.site.view.Base):

    def __call__(self):
        super(RSSFeed, self).__call__()
        self.request.response.content_type = 'application/rss+xml'
        return lxml.etree.tostring(
            self.build_feed(), pretty_print=True, xml_declaration=True,
            encoding='utf8')

    def build_feed(self):
        E = ElementMaker
        root = E.rss(version='2.0')
        channel = E.channel(
            E.title('Spektrum Kooperationsfeed'),
            E.link(self.request.route_url('home')),
            E.description(),
            E.language('de-de'),
            # XXX Is hard-coded okay?
            E.copyright('Copyright ZEIT ONLINE GmbH. Alle Rechte vorbehalten'),
            # Convoluted way of creating a namespaced tag, sigh.
            getattr(E, '{%s}link' % ATOM_NAMESPACE)(
                href=self.request.url,  # XXX Is this correct?
                type=self.request.response.content_type)
        )
        root.append(channel)
        for content in zeit.content.cp.interfaces.ICPFeed(self.context).items:
            image = zeit.content.image.interfaces.IMasterImage(
                zeit.content.image.interfaces.IImages(content).image)
            channel.append(E.item(
                E.title(content.title),
                E.link(zeit.web.core.template.create_url(content)),
                E.description(content.teaserText),
                E.pubDate(format_rfc822_date(
                    last_published_semantic(content))),
                E.guid(content.uniqueId, isPermaLink='false'),
                E.enclosure(
                    url=zeit.web.core.template.default_image_url(
                        image, 'spektrum'),
                    # XXX Incorrect length, since bitblt will resize the image,
                    # but since that happens outside of the application, we
                    # cannot know the real size here.
                    length=str(image.size),
                    type=image.mimeType)
            ))
        return root


def format_rfc822_date(timestamp):
    if timestamp is None:
        timestamp = datetime.min
    return email.utils.formatdate(time.mktime(timestamp.timetuple()))


def last_published_semantic(content):
    return zeit.web.core.view_centerpage.form_date(
        zeit.web.core.view_centerpage.get_last_published_semantic(content))
