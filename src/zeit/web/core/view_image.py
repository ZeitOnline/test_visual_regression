import os.path
import logging

from pyramid.view import view_config
import pyramid.httpexceptions
import pyramid.response
import zope.component

import zeit.cms.interfaces
import zeit.content.image.interfaces

import zeit.web
import zeit.web.core.image
import zeit.web.core.view
import zeit.web.site.area
import zeit.web.site.area.spektrum
import zeit.web.site.area.zett


log = logging.getLogger(__name__)


@view_config(context=zeit.content.image.interfaces.IImage)
class Image(zeit.web.core.view.Base):

    def __call__(self):
        resp = self.request.response
        if self.content_length:
            resp.headers['Content-Length'] = self.content_length
        resp.headers['Content-Disposition'] = self.content_disposition
        resp.headers['Content-Type'] = resp.content_type = self.content_type
        resp.app_iter = pyramid.response.FileIter(self.filehandle)
        resp.cache_expires(zeit.web.core.interfaces.ICachingTime(self.context))
        return resp

    @zeit.web.reify
    def content_disposition(self):
        if self.context.__name__ in self.context.__parent__:
            name = zeit.cms.interfaces.normalize_filename(
                self.context.__name__)
            return 'inline; filename="{}"'.format(name)
        try:
            name = os.path.basename(
                self.context.__parent__.uniqueId.rstrip('/'))
        except:
            name = self.request.path.split('/')[-1]

        ext = self.content_type.split('/')[-1]
        name = zeit.cms.interfaces.normalize_filename(name)
        return 'inline; filename="{}.{}"'.format(name, ext)

    @zeit.web.reify
    def content_type(self):
        try:
            return str(self.context.mimeType)
        except (AttributeError, UnicodeEncodeError):
            return 'image/jpeg'

    @zeit.web.reify
    def content_length(self):
        try:
            self.filehandle.seek(0, 2)
            length = str(self.filehandle.tell())
        except Exception, err:
            log.warning(u'Content-Length indeterminable: {} at {}'.format(
                err.message, self.request.path_qs))
        else:
            return length
        finally:
            self.filehandle.seek(0, 0)

    @zeit.web.reify
    def filehandle(self):
        try:
            return self.context.open()
        except (AttributeError, IOError), err:
            log.warning(u'Image not openable: {} at {}'.format(
                err.message, self.request.path_qs))
            raise pyramid.httpexceptions.HTTPNotFound(err.message)


@view_config(context=zeit.content.video.interfaces.IVideo,
             name='imagegroup')
class Brightcove(Image):

    mapping = {'still.jpg': 'wide__580x326', 'thumbnail.jpg': 'wide__120x67'}

    def __init__(self, context, request):
        super(Brightcove, self).__init__(context, request)
        group = zeit.content.image.interfaces.IImageGroup(self.context)
        variant = request.path_info.rsplit('/', 1).pop()
        try:
            self.context = group[self.mapping.get(variant, variant)]
        except Exception, err:
            raise pyramid.httpexceptions.HTTPNotFound(err.message)


class RSSImage(Image):

    remote_host = ''
    ig_class = zeit.web.core.image.RemoteImageGroup

    def __init__(self, context, request):
        super(RSSImage, self).__init__(context, request)

        segments = self.request.matchdict.get('path')
        if len(segments) < 3:
            raise pyramid.httpexceptions.HTTPNotFound()

        file_name, variant = segments[-2:]
        path = '/'.join(segments[:-1]).encode('utf-8')
        image_url = '{}/{}'.format(self.remote_host, path)

        group = self.ig_class(context)
        group.image_url = image_url
        try:
            self.context = group[variant]
        except Exception, err:
            raise pyramid.httpexceptions.HTTPNotFound(err.message)

    @zeit.web.reify
    def remote_host(self):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        return conf.get(self.host_key, '')


@view_config(route_name='spektrum-image')
class Spektrum(RSSImage):

    host_key = 'spektrum_img_host'
    ig_class = zeit.web.site.area.spektrum.ImageGroup


@view_config(route_name='zett-image')
class Zett(RSSImage):

    host_key = 'zett_img_host'
    ig_class = zeit.web.site.area.zett.ImageGroup
