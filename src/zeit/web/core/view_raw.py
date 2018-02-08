import mimetypes

from pyramid.response import FileIter
from pyramid.response import Response
import magic
import pyramid.httpexceptions

from zeit.connector.interfaces import IResource
import zeit.cms.repository.interfaces
import zeit.content.cp.interfaces
import zeit.content.image.interfaces
import zeit.content.rawxml.interfaces
import zeit.content.text.interfaces

import zeit.web


@zeit.web.view_config(
    context=zeit.cms.repository.interfaces.IUnknownResource)
@zeit.web.view_config(
    context=zeit.content.text.interfaces.IText)
@zeit.web.view_config(
    context=zeit.content.rawxml.interfaces.IRawXML)
@zeit.web.view_config(
    context=zeit.cms.repository.interfaces.IUnknownResource,
    host_restriction=('xml', 'static', 'scripts'))
@zeit.web.view_config(
    context=zeit.content.text.interfaces.IText,
    host_restriction=('xml', 'static', 'scripts'))
@zeit.web.view_config(
    context=zeit.content.rawxml.interfaces.IRawXML,
    host_restriction=('xml', 'static', 'scripts'))
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
        resource = IResource(self.context)
        head = resource.data.read(200)
        resource.data.seek(0)
        with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as m:
            file_type = m.id_buffer(head) or ''
        # Unfortunately, libmagic insists on also reading the file if you want
        # to give it a filename; this does not work for our abstraction level.
        # Fortunately, the stdlib includes a filename-only function.
        if not file_type or file_type.startswith('text/plain'):
            guessed, transfer = mimetypes.guess_type(self.context.__name__)
            if guessed:
                # We keep the charset declaration that magic figured out (if
                # any), since that can't be guessed from the filename. ;)
                file_type = file_type.replace('text/plain', guessed)

        if not file_type:
            raise pyramid.httpexceptions.HTTPNotFound()

        self.request.response.app_iter = FileIter(resource.data)
        self.request.response.content_type = file_type
        self.request.response.headers.add('Access-Control-Allow-Origin', '*')
        return self.request.response


@zeit.web.view_config(
    context=zeit.cms.repository.interfaces.IFile)
@zeit.web.view_config(
    context=zeit.cms.repository.interfaces.IFile,
    host_restriction=('xml', 'static', 'scripts'))
class RawFile(zeit.web.core.view.Base):

    def __call__(self):
        super(RawFile, self).__call__()
        self.request.response.app_iter = FileIter(IResource(self.context).data)
        self.request.response.content_type = self.context.mimeType
        self.request.response.headers.add('Access-Control-Allow-Origin', '*')
        return self.request.response
