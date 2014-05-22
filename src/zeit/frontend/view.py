from babel.dates import get_timezone
from pyramid.response import Response
from pyramid.view import notfound_view_config
from pyramid.view import view_config
from zeit.cms.workflow.interfaces import IPublishInfo
import logging
import os.path
import pyramid.response
import zeit.connector.connector
import zeit.connector.interfaces
import zeit.content.cp.interfaces
import zeit.content.article.interfaces
import zeit.content.image.interfaces
import zeit.frontend.article
import zope.component
import urllib2

log = logging.getLogger(__name__)


class Base(object):

    """Base class for all views."""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.request.response.cache_expires(300)

    def __call__(self):
        return {}

    @property
    def type(self):
        return type(self.context).__name__.lower()

    @property
    def ressort(self):
        if self.context.ressort:
            return self.context.ressort.lower()
        else:
            return ''

    @property
    def sub_ressort(self):
        if self.context.sub_ressort:
            return self.context.sub_ressort.lower()
        else:
            return ''

    @property
    def banner_channel(self):
        channel = ''
        if self.ressort:
            myressort = self.ressort.replace('zeit-magazin', 'zeitmz')
            # TODO: end discrepance between testing and live ressports!
            myressort = myressort.replace('lebensart', 'zeitmz')
            channel += myressort
        if self.sub_ressort:
            channel += "/" + self.sub_ressort.replace('-', 'und', 1)
        if self.type:
            # TODO: zone type gallery after launch
            mytype = self.type.replace('gallery', 'article')
            channel += "/" + mytype
        return channel

    def banner(self, tile):
        try:
            return zeit.frontend.banner.banner_list[tile - 1]
        except IndexError:
            return None


class Content(Base):
    _navigation = {'start': ('Start', 'http://www.zeit.de/index', 'myid1'),
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
                   ), }

    @property
    def title(self):
        return self.context.title

    @property
    def subtitle(self):
        return self.context.subtitle

    @property
    def supertitle(self):
        return self.context.supertitle

    @property
    def pagetitle(self):
        # Fallback gracefully if title or supertitle is missing.
        tokens = (self.context.supertitle, self.context.title)
        return ': '.join([t for t in tokens if t])

    @property
    def pagedescription(self):
        return self.context.subtitle

    @property
    def rankedTags(self):
        return self.context.keywords

    @property
    def rankedTagsList(self):
        keyword_list = ''
        if self.rankedTags:
            for keyword in self.context.keywords:
                keyword_list += keyword.label + ';'
            return keyword_list[:-1]
        else:
            return ''

    @property
    def show_article_date(self):
        if self.date_last_published_semantic:
            return self.date_last_published_semantic
        else:
            return self.date_first_released

    @property
    def date_first_released(self):
        tz = get_timezone('Europe/Berlin')
        date = IPublishInfo(
            self.context).date_first_released
        if date:
            return date.astimezone(tz)

    @property
    def date_first_released_meta(self):
        return IPublishInfo(
            self.context).date_first_released.isoformat()

    @property
    def date_last_published_semantic(self):
        tz = get_timezone('Europe/Berlin')
        date = IPublishInfo(self.context).date_last_published_semantic
        if self.date_first_released is not None and date is not None:
            if date > self.date_first_released:
                return date.astimezone(tz)
            else:
                return None

    def _get_date_format(self):
        if self.context.product:
            if self.context.product.id == 'ZEI' or \
               self.context.product.id == 'ZMLB':
                return 'short'
            else:
                return 'long'
        else:
            return 'long'

    @property
    def show_date_format(self):
        if self.date_last_published_semantic:
            return 'long'
        else:
            return self._get_date_format()

    @property
    def show_date_format_seo(self):
        return self._get_date_format()

    @property
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
    return Response('OK', 200)


@notfound_view_config(request_method='GET')
def notfound_get(request):
    try:
        request = urllib2.Request('http://www.zeit.de/error/404')
        response = urllib2.urlopen(request, timeout=4)
        html = response.read()
        return Response(html, status='404 Not Found')
    except urllib2.URLError:
        return Response('Status 404:Dokument nicht gefunden.',
                        status='404 Not Found')
