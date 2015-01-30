import urllib2

from pyramid.view import view_config
import pyramid.httpexceptions
import pyramid.response

import zeit.web.site.spektrum
import zeit.web.core.view


@view_config(route_name='spektrum-image')
class SpektrumImage(zeit.web.core.view.Base):
    def __call__(self):
        path = '/'.join(self.request.matchdict.get('path'))
        image_url = 'http://www.spektrum.de/{}'.format(path)
        _, file_name = path.rsplit('/', 1)

        try:
            fileobj = urllib2.urlopen(image_url, timeout=4)
        except IOError:
            raise pyramid.httpexceptions.HTTPNotFound()

        response = self.request.response
        response.app_iter = pyramid.response.FileIter(fileobj)
        response.cache_expires(60 * 60 * 24 * 365)
        response.content_type = fileobj.headers.get('Content-Type')
        response.headers['Content-Type'] = response.content_type
        response.headers['Content-Disposition'] = (
            'inline; filename="{}"'.format(file_name).encode('utf8'))
        return response
