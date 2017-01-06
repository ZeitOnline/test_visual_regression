import logging

from pyramid.response import FileIter
from pyramid.response import Response
import lxml.etree
import lxml.objectify
import magic
import pyramid.httpexceptions

from zeit.connector.interfaces import IResource
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.content.article.interfaces
import zeit.content.author.interfaces
import zeit.content.cp.interfaces
import zeit.content.gallery.interfaces
import zeit.content.link.interfaces
import zeit.content.video.interfaces

import zeit.web
import zeit.web.core.article
import zeit.web.core.view


log = logging.getLogger(__name__)


class XMLContent(zeit.web.core.view.Base):

    def __call__(self):
        super(XMLContent, self).__call__()
        self.request.response.content_type = 'application/xml'
        self.request.response.charset = 'iso-8859-1'
        self.request.response.headers['Access-Control-Allow-Origin'] = '*'
        self._include_infoboxes()
        self._include_liveblogs()
        self._set_meta_robots()
        self._set_mobile_alternative()
        lxml.objectify.deannotate(
            self.xml, pytype=True, xsi=True, xsi_nil=True)
        return lxml.etree.tostring(
            self.xml, pretty_print=True, xml_declaration=True,
            # XXX A sin we inherited from XSLT.
            encoding='iso-8859-1')

    def _include_infoboxes(self):
        for infobox in self.xml.xpath('/article/body/division/infobox'):
            box = zeit.cms.interfaces.ICMSContent(infobox.get('href'), None)
            if not zeit.content.infobox.interfaces.IInfobox.providedBy(box):
                log.info(
                    'Cannot resolve infobox %s, ignored.', infobox.get('href'))
                continue
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


class CenterpageMixin(object):

    @property
    def xml(self):
        return zeit.content.cp.interfaces.IRenderedXML(self.context)


# NOTE: Pyramid route specififity is an obscure topic. We try to configure
#       the XML routes as specific as our HTML ones with dummy predicates (ND)


@zeit.web.view_defaults(
    header='host:xml(\.staging)?\.zeit\.de',
    custom_predicates=(lambda *_: True,),
    renderer='string',
    request_method='GET')
@zeit.web.view_config(context=zeit.cms.content.interfaces.IXMLContent)
@zeit.web.view_config(
    context=zeit.content.article.interfaces.IArticle,
    custom_predicates=(lambda *_: True, lambda *_: True, lambda *_: True))
@zeit.web.view_config(context=zeit.content.author.interfaces.IAuthor)
@zeit.web.view_config(context=zeit.content.gallery.interfaces.IGallery)
@zeit.web.view_config(context=zeit.content.link.interfaces.ILink)
@zeit.web.view_config(context=zeit.content.video.interfaces.IVideo)
@zeit.web.view_config(context=zeit.web.core.article.IColumnArticle)
@zeit.web.view_config(context=zeit.web.core.article.ILiveblogArticle)
@zeit.web.view_config(context=zeit.web.core.article.ILongformArticle)
@zeit.web.view_config(context=zeit.web.core.article.IPhotoclusterArticle)
@zeit.web.view_config(context=zeit.web.core.article.IShortformArticle)
class HostHeaderContent(XMLContent):
    pass


@zeit.web.view_config(context=zeit.content.cp.interfaces.ICenterPage)
@zeit.web.view_config(context=zeit.content.cp.interfaces.ICP2009)
@zeit.web.view_config(context=zeit.content.cp.interfaces.ICP2015)
class HostHeaderCP(CenterpageMixin, HostHeaderContent):
    pass


@zeit.web.view_defaults(
    route_name='xml',
    custom_predicates=(lambda *_: True,),
    renderer='string',
    request_method='GET')
@zeit.web.view_config(context=zeit.cms.content.interfaces.IXMLContent)
@zeit.web.view_config(context=zeit.content.article.interfaces.IArticle)
@zeit.web.view_config(context=zeit.content.author.interfaces.IAuthor)
@zeit.web.view_config(context=zeit.content.gallery.interfaces.IGallery)
@zeit.web.view_config(context=zeit.content.link.interfaces.ILink)
@zeit.web.view_config(context=zeit.content.video.interfaces.IVideo)
@zeit.web.view_config(context=zeit.web.core.article.IColumnArticle)
@zeit.web.view_config(context=zeit.web.core.article.ILiveblogArticle)
@zeit.web.view_config(context=zeit.web.core.article.ILongformArticle)
@zeit.web.view_config(context=zeit.web.core.article.IPhotoclusterArticle)
@zeit.web.view_config(context=zeit.web.core.article.IShortformArticle)
class RouteNameContent(XMLContent):
    pass


@zeit.web.view_config(context=zeit.content.cp.interfaces.ICenterPage)
@zeit.web.view_config(context=zeit.content.cp.interfaces.ICP2009)
@zeit.web.view_config(context=zeit.content.cp.interfaces.ICP2015)
class RouteNameCP(CenterpageMixin, RouteNameContent):
    pass


@zeit.web.view_defaults(
    context=zeit.cms.repository.interfaces.IDAVContent,
    custom_predicates=(lambda *_: True,),
    renderer='string',
    request_method='GET')
@zeit.web.view_config(
    route_name='xml')
@zeit.web.view_config(
    header='host:xml(\.staging)?\.zeit\.de')
class NonXMLContent(zeit.web.core.view.Base):

    def __call__(self):
        super(NonXMLContent, self).__call__()
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
