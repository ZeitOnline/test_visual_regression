import os.path
import logging
import urllib2

from pyramid.view import view_config
import pyramid.httpexceptions
import pyramid.response
import zope.component

import zeit.cms.interfaces
import zeit.connector.interfaces
import zeit.content.image.interfaces

import zeit.web
import zeit.web.core.cache
import zeit.web.core.view


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
        resp.cache_expires(zeit.web.core.cache.ICachingTime(self.context))
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
            name = self.request.traversed[-1]

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


@view_config(route_name='spektrum-image')
class SpektrumImage(zeit.web.core.view.Base):

    def __call__(self):
        path = '/'.join(self.request.matchdict.get('path')).encode('utf-8')
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        image_url = '{}/{}'.format(conf.get('spektrum_img_host', ''), path)
        file_name = path.rsplit('/', 1).pop()

        try:
            with zeit.web.core.metrics.timer('spektrum.reponse_time'):
                fileobj = urllib2.urlopen(image_url, timeout=4)
        except IOError:
            raise pyramid.httpexceptions.HTTPNotFound()

        response = self.request.response
        response.app_iter = pyramid.response.FileIter(fileobj)
        response.content_type = 'image/jpeg'
        response.headers['Content-Type'] = response.content_type
        response.headers['Content-Disposition'] = (
            'inline; filename="{}"'.format(file_name))
        response.cache_expires(zeit.web.core.cache.ICachingTime(image_url))
        return response
