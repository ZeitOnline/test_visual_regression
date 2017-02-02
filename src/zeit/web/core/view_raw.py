from pyramid.response import FileIter
from pyramid.response import Response
import magic
import pyramid.httpexceptions

from zeit.connector.interfaces import IResource
import zeit.cms.repository.interfaces

import zeit.web


@zeit.web.view_config(
    context=zeit.cms.repository.interfaces.IUnknownResource)
@zeit.web.view_config(
    context=zeit.content.text.interfaces.IText)
@zeit.web.view_config(
    context=zeit.cms.repository.interfaces.IUnknownResource,
    host_restriction=('xml', 'static', 'scripts', 'zeus'))
@zeit.web.view_config(
    context=zeit.content.text.interfaces.IText,
    host_restriction=('xml', 'static', 'scripts', 'zeus'))
@zeit.web.view_config(
    context=zeit.content.image.interfaces.IImage,
    host_restriction='xml')
class RawContent(zeit.web.core.view.Base):
    """Content that does not have a type that zeit.web especially recognizes is
    served raw. This includes resources without any type, as well as
    zeit.content.text objects.
    """

    def __call__(self):
        super(RawContent, self).__call__()
        head = IResource(self.context).data.read(200)
        IResource(self.context).data.close()
        with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as m:
            file_type = m.id_buffer(head)
        if file_type:
            response = Response(
                app_iter=FileIter(IResource(self.context).data),
                content_type=file_type)
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
        else:
            raise pyramid.httpexceptions.HTTPNotFound()
