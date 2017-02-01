from pyramid.response import FileIter
from pyramid.response import Response
import magic
import pyramid.httpexceptions

from zeit.connector.interfaces import IResource
import zeit.cms.repository.interfaces

import zeit.web


@zeit.web.view_config(context=zeit.cms.repository.interfaces.IDAVContent)
# Even though no host_restriction means "all hosts", we need to explicitly
# declare xml so it meshes with the other views in z.w.core.view_xml.
@zeit.web.view_config(
    context=zeit.cms.repository.interfaces.IDAVContent,
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
