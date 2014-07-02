import os.path
import urllib2

from babel.dates import get_timezone
from pyramid.decorator import reify
from pyramid.view import notfound_view_config
from pyramid.view import view_config
import pyramid.response
import zope.component

import zeit.cms.workflow.interfaces
import zeit.connector.connector
import zeit.connector.interfaces
import zeit.content.article.interfaces
import zeit.content.cp.interfaces
import zeit.content.image.interfaces

import zeit.frontend.article


class Base(object):
    """Base class for all views."""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.request.response.cache_expires(300)

    def __iter__(self):
    # extend if needed
        return iter(['banner_channel',
                    'ressort', 'sub_ressort', 'type'])

    def __call__(self):
        return {}

    @reify
    def type(self):
        return type(self.context).__name__.lower()

    @reify
    def ressort(self):
        if self.context.ressort:
            return self.context.ressort.lower()
        else:
            return ''

    @reify
    def sub_ressort(self):
        if self.context.sub_ressort:
            return self.context.sub_ressort.lower()
        else:
            return ''

    @reify
    def banner_channel(self):
        channel = ''
        if self.ressort:
            myressort = self.ressort.replace('zeit-magazin', 'zeitmz')
            # TODO: End discrepancy between testing and live ressorts!
            myressort = myressort.replace('lebensart', 'zeitmz')
            channel += myressort
        if self.sub_ressort:
            channel += '/' + self.sub_ressort.replace('-', 'und', 1)
        if self.type:
            # TODO: Zone type gallery after launch
            channel += '/' + self.type.replace('gallery', 'article')
        return channel

    def banner(self, tile):
        try:
            return zeit.frontend.banner.banner_list[tile - 1]
        except IndexError:
            return None

    @reify
    def title(self):
        return self.context.title

    @reify
    def supertitle(self):
        return self.context.supertitle

    @reify
    def pagetitle(self):
        seo = zeit.seo.interfaces.ISEO(self.context)
        default = 'ZEITmagazin ONLINE - Mode & Design, Essen & Trinken, Leben'
        if seo.html_title:
            return seo.html_title
        tokens = (self.supertitle, self.title)
        return ': '.join([t for t in tokens if t]) or default

    @reify
    def pagedescription(self):
        default = 'ZEITmagazin ONLINE - Mode & Design, Essen & Trinken, Leben'
        seo = zeit.seo.interfaces.ISEO(self.context)
        if seo.html_description:
            return seo.html_description
        if self.context.subtitle:
            return self.context.subtitle
        return default

    @reify
    def rankedTags(self):
        return self.context.keywords

    @reify
    def rankedTagsList(self):
        if self.rankedTags:
            return ';'.join([rt.label for rt in self.rankedTags])
        else:
            default_tags = [self.context.ressort, self.context.sub_ressort]
            return ';'.join([dt for dt in default_tags if dt])

    @reify
    def is_hp(self):
        return self.request.path == '/' + self.request.registry.settings.hp

    @reify
    def iqd_mobile_settings(self):
        iqd_ids = zeit.frontend.banner.iqd_mobile_ids
        if self.is_hp:
            return getattr(iqd_ids['hp'], 'centerpage')
        try:
            return getattr(iqd_ids[self.sub_ressort], self.type,
                           getattr(iqd_ids[self.sub_ressort], 'default'))
        except KeyError:
            return {}


class Content(Base):
    _navigation = {
        'start': (
            'Start',
            'http://www.zeit.de/index',
            'myid1'
        ),
        'zmo': (
            'ZEIT Magazin',
            'http://www.zeit.de/zeit-magazin/index',
            'myid_zmo',
        ),
        'leben': (
            'Leben',
            'http://www.zeit.de/zeit-magazin/leben/index',
            'myid2',
        ),
        'mode-design': (
            'Mode & Design',
            'http://www.zeit.de/zeit-magazin/mode-design/index',
            'myid3',
        ),
        'essen-trinken': (
            'Essen & Trinken',
            'http://www.zeit.de/zeit-magazin/essen-trinken/index',
            'myid4',
        )
    }

    @reify
    def subtitle(self):
        return self.context.subtitle

    @reify
    def show_article_date(self):
        return self.date_last_published_semantic or self.date_first_released

    @reify
    def date_first_released(self):
        tz = get_timezone('Europe/Berlin')
        date = zeit.cms.workflow.interfaces.IPublishInfo(
            self.context).date_first_released
        if date:
            return date.astimezone(tz)

    @reify
    def date_first_released_meta(self):
        return zeit.cms.workflow.interfaces.IPublishInfo(
            self.context).date_first_released.isoformat()

    @reify
    def date_last_published_semantic(self):
        tz = get_timezone('Europe/Berlin')
        date = zeit.cms.workflow.interfaces.IPublishInfo(
            self.context).date_last_published_semantic
        if self.date_first_released is not None and date is not None:
            if date > self.date_first_released:
                return date.astimezone(tz)
            else:
                return None

    @reify
    def date_format(self):
        if self.context.product:
            if self.context.product.id == 'ZEI' or \
               self.context.product.id == 'ZMLB':
                return 'short'
        return 'long'

    @reify
    def show_date_format(self):
        if self.date_last_published_semantic:
            return 'long'
        else:
            return self.date_format

    @reify
    def show_date_format_seo(self):
        return self.date_format

    @reify
    def breadcrumb(self):
        crumb = self._navigation
        l = [crumb['start']]
        l.append(crumb['zmo'])
        if self.context.ressort in crumb:
            l.append(crumb[self.context.ressort])
        if self.context.sub_ressort in crumb:
            l.append(crumb[self.context.sub_ressort])
        if self.title:
            l.append((self.title, ''))
        return l


@view_config(context=zeit.content.image.interfaces.IImage)
class Image(Base):

    def __call__(self):
        connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        if not isinstance(connector, zeit.connector.connector.Connector):
            # Default case: filesystem. We can avoid loading the image
            # contents into memory here, and instead simply tell the web server
            # to stream out the file by giving its absolute path.
            repository_path = connector.repository_path
            if not repository_path.endswith('/'):
                repository_path += '/'
            response = pyramid.response.FileResponse(
                self.context.uniqueId.replace(
                    'http://xml.zeit.de/', repository_path),
                content_type=self.context.mimeType)
        else:
            # Special case for DAV (preview environment)
            response = self.request.response
            response.app_iter = pyramid.response.FileIter(self.context.open())

        # Workaround for <https://github.com/Pylons/webob/issues/130>
        response.content_type = self.context.mimeType.encode('utf-8')
        response.headers['Content-Type'] = response.content_type
        response.headers['Content-Length'] = str(self.context.size)
        response.headers['Content-Disposition'] = 'inline; filename="%s"' % (
            os.path.basename(self.context.uniqueId).encode('utf8'))
        return response


@view_config(route_name='health_check')
def health_check(request):
    return pyramid.response.Response('OK', 200)


@notfound_view_config(request_method='GET')
def notfound_get(request):
    try:
        request = urllib2.Request('http://www.zeit.de/error/404')
        response = urllib2.urlopen(request, timeout=4)
        html = response.read()
        return pyramid.response.Response(html, status='404 Not Found')
    except urllib2.URLError:
        return pyramid.response.Response('Status 404:Dokument nicht gefunden.',
                                         status='404 Not Found')
