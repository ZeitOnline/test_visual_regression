import os.path
import logging
import urllib2

from pyramid.view import view_config
import pyramid.httpexceptions
import pyramid.response
import zope.component

import zeit.connector.interfaces
import zeit.content.image.interfaces

import zeit.web
import zeit.web.core.view


log = logging.getLogger(__name__)


@view_config(context=zeit.content.image.interfaces.IImage)
class Image(zeit.web.core.view.Base):

    def __call__(self):
        resp = self.request.response
        resp.headers['Content-Length'] = self.content_length
        resp.headers['Content-Disposition'] = self.content_disposition
        resp.headers['Content-Type'] = resp.content_type = self.content_type
        resp.app_iter = pyramid.response.FileIter(self.filehandle)
        resp.cache_expires(zeit.web.core.cache.ICachingTime(self.context))
        return resp

    @zeit.web.reify
    def content_disposition(self):
        if self.context.__name__ in self.context.__parent__:
            return 'inline; filename="{}"'.format(self.context.__name__)
        try:
            name = os.path.basename(
                self.context.__parent__.uniqueId.rstrip('/'))
        except:
            name = self.request.traversed[-1]
        try:
            ext = self.content_type.split('/')[-1]
        except:
            ext = 'jpeg'
        return 'inline; filename="{}.{}"'.format(
            name.encode('utf8', 'ignore'), ext)

    @zeit.web.reify
    def content_type(self):
        return self.context.mimeType.encode('utf-8')

    @zeit.web.reify
    def content_length(self):
        try:
            self.filehandle.seek(0, 2)
            mime = str(self.filehandle.tell())
        except Exception, err:
            log.warning(u'Content-Length indeterminable: {} at {}'.format(
                err.message, self.request.path_qs))
        else:
            return mime
        finally:
            self.filehandle.seek(0, 0)

    @zeit.web.reify
    def filehandle(self):
        try:
            return self.context.open()
        except AttributeError, err:
            log.warning(u'Image not openable: {} at {}'.format(
                err.message, self.request.path_qs))
            raise pyramid.httpexceptions.HTTPNotFound(err.message)


@view_config(context=zeit.content.video.interfaces.IVideo,
             name='imagegroup',
             path_info='.*imagegroup/(still|thumbnail).jpg')
class Brightcove(zeit.web.core.view.Base):

    def __call__(self):
        _, file_name = self.request.path_info.rsplit('/', 1)
        group = zeit.content.image.interfaces.IImageGroup(self.context)
        image = group[file_name]

        response = self.request.response
        response.app_iter = pyramid.response.FileIter(image.image.open())
        response.content_type = image.mimeType
        response.headers['Content-Type'] = response.content_type
        response.headers['Content-Disposition'] = (
            'inline; filename="{}"'.format(file_name))
        response.cache_expires(zeit.web.core.cache.ICachingTime(self.context))
        return response


@view_config(route_name='spektrum-image')
class SpektrumImage(zeit.web.core.view.Base):

    def __call__(self):
        path = '/'.join(self.request.matchdict.get('path'))
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        image_url = '{}/{}'.format(conf.get('spektrum_img_host', ''), path)
        _, file_name = path.rsplit('/', 1)

        try:
            fileobj = urllib2.urlopen(image_url, timeout=4)
        except IOError:
            raise pyramid.httpexceptions.HTTPNotFound()

        response = self.request.response
        response.app_iter = pyramid.response.FileIter(fileobj)
        response.content_type = 'image/jpeg'
        response.headers['Content-Type'] = response.content_type
        response.headers['Content-Disposition'] = (
            'inline; filename="{}"'.format(file_name).encode('utf8'))
        response.cache_expires(zeit.web.core.cache.ICachingTime(image_url))
        return response
