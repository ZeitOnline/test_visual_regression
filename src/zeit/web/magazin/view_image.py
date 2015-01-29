import os.path

from pyramid.view import view_config
import pyramid.response
import zope.component

import zeit.connector.interfaces
import zeit.content.image.interfaces

import zeit.web.core.view


@view_config(context=zeit.content.image.interfaces.IImage)
class Image(zeit.web.core.view.Base):

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

        response.content_type = self.context.mimeType.encode('utf-8')
        response.headers['Content-Type'] = response.content_type
        response.headers['Content-Length'] = str(self.context.size)
        response.headers['Content-Disposition'] = 'inline; filename="%s"' % (
            os.path.basename(self.context.uniqueId).encode('utf8'))
        return response


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
        return response
