from pyramid.response import FileIter
from pyramid.response import Response
from zeit.connector.interfaces import IResource
import lxml.etree
import lxml.objectify
import magic
import pyramid.view
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.content.cp.interfaces


@pyramid.view.view_defaults(
    context=zeit.cms.content.interfaces.IXMLContent,
    renderer='string')
@pyramid.view.view_config(
    route_name='xml')
@pyramid.view.view_config(
    header='host:xml(\.staging)?\.zeit\.de')
class XMLContent(zeit.web.core.view.Base):

    allowed_on_hosts = ['xml']

    def __call__(self):
        super(XMLContent, self).__call__()
        self.request.response.content_type = 'application/xml'
        self.request.response.charset = 'iso-8859-1'
        self._include_infoboxes()
        self._include_liveblogs()
        self._set_meta_robots()
        self._set_mobile_alternative()
        return lxml.etree.tostring(
            self.deannotate(self.xml), pretty_print=True, xml_declaration=True,
            # XXX A sin we inherited from XSLT.
            encoding='iso-8859-1')

    def _include_infoboxes(self):
        for infobox in self.xml.xpath('/article/body/division/infobox'):
            box = zeit.cms.interfaces.ICMSContent(infobox.get('href'))
            lxml.objectify.SubElement(infobox, 'container')
            infobox.container = box.xml
            infobox.set(
                'publication-date', infobox.get('publication-date', ''))
            infobox.set('expires', infobox.get('expires', ''))

    def _include_liveblogs(self):
        for liveblog in self.xml.xpath('/article/body/division/liveblog'):
            el = lxml.objectify.SubElement(
                liveblog, '{http://www.edge-delivery.org/esi/1.0}include',
                nsmap={'esi': 'http://www.edge-delivery.org/esi/1.0'})
            url = 'http://www.zeit.de/liveblog-backend/{}.html'.format(
                liveblog.get('blogID', ''))
            el.set('src', url)
            liveblog.set('data-type', 'esi-content')
            liveblog.attrib.pop('blogID')
            liveblog.tag = 'div'

    def _set_mobile_alternative(self):
        metadata = zeit.cms.content.interfaces.ICommonMetadata(
            self.context, None)
        mobile_alternative = (metadata.mobile_alternative
                              if metadata is not None else None)
        if mobile_alternative:
            self.request.response.headers.add(
                'X-MobileAlternative', mobile_alternative)

    def _set_meta_robots(self):
        sync = zeit.cms.content.interfaces.IDAVPropertyXMLSynchroniser(
            self.context, None)
        if sync is None:
            return
        robots_prop = zeit.seo.seo.SEO.meta_robots
        sync.set(
            'http://namespaces.zeit.de/CMS/meta', robots_prop.name,
            self.meta_robots)

    @property
    def ressort(self):
        return None

    @property
    def xml(self):
        return self.context.xml

    def deannotate(self, xml):
        lxml.objectify.deannotate(
            xml, pytype=True, xsi=True, xsi_nil=True)
        return xml


@pyramid.view.view_defaults(
    context=zeit.content.cp.interfaces.ICenterPage,
    renderer='string')
@pyramid.view.view_config(
    route_name='xml')
@pyramid.view.view_config(
    header='host:xml(\.staging)?\.zeit\.de')
class Centerpage(XMLContent):

    @property
    def xml(self):
        return zeit.content.cp.interfaces.IRenderedXML(self.context)


@pyramid.view.view_defaults(
    context=zeit.cms.repository.interfaces.IDAVContent,
    renderer='string')
@pyramid.view.view_config(
    route_name='xml')
@pyramid.view.view_config(
    header='host:xml(\.staging)?\.zeit\.de')
class NonXMLContent(zeit.web.core.view.Base):

    allowed_on_hosts = ['xml']

    def __call__(self):
        super(NonXMLContent, self).__call__()
        head = IResource(self.context).data.read(200)
        IResource(self.context).data.close()
        with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as m:
            file_type = m.id_buffer(head)
        if file_type:
            return Response(
                app_iter=FileIter(IResource(self.context).data),
                content_type=file_type)
        else:
            raise pyramid.httpexceptions.HTTPNotFound()
