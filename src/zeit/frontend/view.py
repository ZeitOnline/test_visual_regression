from babel.dates import get_timezone
from datetime import date
from pyramid.renderers import render_to_response
from pyramid.view import view_config
from zeit.cms.workflow.interfaces import IPublishInfo, IModified
from zeit.content.article.edit.interfaces import IImage
from zeit.content.article.edit.interfaces import IVideo
from zeit.content.image.interfaces import IImageMetadata
from zeit.frontend.log import access_log
from zeit.magazin.interfaces import IArticleTemplateSettings, INextRead
from zope.component import providedBy
import logging
import os.path
import pyramid.response
import zeit.connector.connector
import zeit.connector.interfaces
import zeit.content.article.interfaces
import zeit.content.image.interfaces
import zope.component

log = logging.getLogger(__name__)


class Base(object):
    """Base class for all views."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        access_log.info(self.request.url)
        return {}


_navigation = {'start': ('Start', 'http://www.zeit.de/index', 'myid1'),
               'zmo': ('ZEIT Magazin', 'http://www.zeit.de/index', 'myid_zmo'),
               'lebensart': (
                   'ZEIT Magazin',
                   'http://www.zeit.de/magazin/index',
                   'myid2',
               ),
               'mode': (
                   'Mode',
                   'http://www.zeit.de/magazin/lebensart/index',
                   'myid3',
               ), }


@view_config(route_name='json',
             context=zeit.content.article.interfaces.IArticle,
             renderer='json')
@view_config(context=zeit.content.article.interfaces.IArticle,
             renderer='templates/article.html')
class Article(Base):

    def __call__(self):
        super(Article, self).__call__()
        self.context.advertising_enabled = True
        self.context.main_nav_full_width = False
        self.context.is_longform = False
        self.context.current_year = date.today().year

        if IArticleTemplateSettings(self.context).template == 'longform':
            self.context.advertising_enabled = False
            self.context.main_nav_full_width = True
            self.context.is_longform = True
            return render_to_response('templates/longform.html',
                                      {"view": self},
                                      request=self.request)
        if IArticleTemplateSettings(self.context).template == 'photocluster':
            self.context.advertising_enabled = False
            return render_to_response('templates/photocluster.html',
                                      {"view": self},
                                      request=self.request)
        return {}

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
    def pages(self):
        return zeit.frontend.interfaces.IPages(self.context)

    @property
    def _select_first_body_obj(self):
        body = zeit.content.article.edit.interfaces.IEditableBody(self.context)
        return body.values().pop(0) if len(body.values()) > 0 else None

    def _create_obj(self, _cls, obj):
        try:
            return _cls(obj)
        except OSError:
            log.debug("Object does not exist.")

    @property
    def header_img(self):
        obj = self._select_first_body_obj
        if IImage in providedBy(obj):
            return self._create_obj(zeit.frontend.block.HeaderImage, obj)

    @property
    def header_video(self):
        obj = self._select_first_body_obj
        if IVideo in providedBy(obj):
            return self._create_obj(zeit.frontend.block.HeaderVideo, obj)

    @property
    def first_img(self):
        obj = self._select_first_body_obj
        if IImage in providedBy(obj):
            return self._create_obj(zeit.frontend.block.Image, obj)

    @property
    def header_elem(self):
        if self.header_video is not None:
            return self.header_video
        return self.header_img

    @property
    def sharing_img(self):
        if self.header_img is not None:
            return self.header_img
        return self.first_img

    @property
    def author(self):
        try:
            author = self.context.authorships[0].target
        except (IndexError, OSError):
            author = None
        return {
            'name': author.display_name if author else None,
            'href': author.uniqueId if author else None,
            'prefix': " von " if self.context.genre else "Von ",
            'suffix': ', ' if self.location else None,
        }

    @property
    def publish_date(self):
        tz = get_timezone('Europe/Berlin')
        date = IPublishInfo(
            self.context).date_last_published_semantic
        if date:
            return date.astimezone(tz)

    @property
    def publish_date_meta(self):
        return IPublishInfo(
            self.context).date_last_published_semantic.isoformat()

    @property
    def last_modified_date(self):
        return IModified(self.context).date_last_modified

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
    def genre(self):
        return self.context.genre

    @property
    def source(self):
        return self.context.copyrights or self.context.product_text

    @property
    def location(self):
        return None  # XXX not implemented in zeit.content.article yet

    @property
    def focussed_nextread(self):
        nextread = INextRead(self.context)
        related = nextread.nextread
        if related:
            image = related.main_image
            if image is not None:
                image = {
                    'uniqueId': image.uniqueId,
                    'caption': (related.main_image_block.custom_caption
                                or IImageMetadata(image).caption),
                }
            else:
                image = {'uniqueId': None}
            return {'layout': nextread.nextread_layout,
                    'article': related,
                    'image': image}

    @property
    def breadcrumb(self):
        l = [_navigation['start']]
        l.append(_navigation['zmo'])
        if self.context.ressort in _navigation:
            l.append(_navigation[self.context.ressort])
        if self.context.sub_ressort in _navigation:
            l.append(_navigation[self.context.sub_ressort])
        if self.title:
            l.append((self.title, 'http://localhost'))
        return l

    @property
    def tracking_type(self):
        if type(self.context).__name__.lower() == 'article':
            return 'Artikel'

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
    def text_length(self):
        return self.context.textLength

    @property
    def banner_channel(self):
        channel = ''
        if self.ressort:
            channel += self.ressort
        if self.sub_ressort:
            channel += "/" + self.sub_ressort
        if self.type:
            channel += "/" + self.type
        return channel

    @property
    def banner(self):
        # faking banner xml (mvp yeah you know me)
        return {
            'superbanner': {
                'name': 'superbanner',
                'tile': '1',
                'sizes': ['728x90'],
                'dcopt': 'ist',
                'label': 'anzeige',
                'noscript_width_height': ('728', '90'),
                'diuqilon': True,
                'min_width': 768
            },
            'skyscraper': {
                'name': 'skyscraper',
                'tile': '2',
                'sizes': ['120x600'],
                'dcopt': 'ist',
                'adlabel': 'Anzeige',
                'noscript_width_height': ('120','600'),
                'diuqilon': True,
                'min_width': 768
            },
        }


@view_config(route_name='json',
             context=zeit.content.article.interfaces.IArticle,
             renderer='json', name='teaser')
@view_config(name='teaser',
             context=zeit.content.article.interfaces.IArticle,
             renderer='templates/teaser.html')
class Teaser(Article):

    @property
    def teaser_text(self):
        """docstring for teaser"""
        return self.context.teaser


@view_config(context=zeit.content.image.interfaces.IImage)
class Image(Base):

    def __call__(self):
        super(Image, self).__call__()
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
