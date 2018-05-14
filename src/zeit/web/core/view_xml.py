import logging

import lxml.etree
import lxml.objectify
import zope.component

import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.content.article.interfaces
import zeit.content.author.interfaces
import zeit.content.cp.interfaces
import zeit.content.gallery.interfaces
import zeit.content.link.interfaces
import zeit.content.video.interfaces

import zeit.web
import zeit.web.core.article
import zeit.web.core.interfaces
import zeit.web.core.view


log = logging.getLogger(__name__)


# Note: One might think it would be sleeker to set the host_restriction as a
#       view_default. That would be a great idea, if not for the excruciating
#       convultion that is pyramid view predicate discrimination.

@zeit.web.view_defaults(renderer='string')
@zeit.web.view_config(context=zeit.content.author.interfaces.IAuthor,
                      host_restriction='xml')
@zeit.web.view_config(context=zeit.content.gallery.interfaces.IGallery,
                      host_restriction='xml')
@zeit.web.view_config(context=zeit.content.link.interfaces.ILink,
                      host_restriction='xml')
@zeit.web.view_config(context=zeit.content.video.interfaces.IVideo,
                      host_restriction='xml')
class XMLContent(zeit.web.core.view.Base):

    def __call__(self):
        super(XMLContent, self).__call__()
        self.request.response.content_type = 'application/xml'
        self.request.response.charset = 'iso-8859-1'
        self.request.response.headers['Access-Control-Allow-Origin'] = '*'
        self._set_meta_robots()
        self._set_mobile_alternative()
        lxml.objectify.deannotate(
            self.xml, pytype=True, xsi=True, xsi_nil=True)
        return lxml.etree.tostring(
            self.xml, pretty_print=True, xml_declaration=True,
            # XXX A sin we inherited from XSLT.
            encoding='iso-8859-1')

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
    def xml(self):
        return self.context.xml


@zeit.web.view_config(context=zeit.content.article.interfaces.IArticle,
                      host_restriction='xml')
@zeit.web.view_config(context=zeit.web.core.article.ILiveblogArticle,
                      host_restriction='xml')
@zeit.web.view_config(context=zeit.web.core.article.IColumnArticle,
                      host_restriction='xml')
@zeit.web.view_config(context=zeit.web.magazin.article.ILongformArticle,
                      host_restriction='xml')
@zeit.web.view_config(context=zeit.web.magazin.article.IPhotoclusterArticle,
                      host_restriction='xml')
@zeit.web.view_config(context=zeit.web.magazin.article.IShortformArticle,
                      host_restriction='xml')
@zeit.web.view_config(context=zeit.web.magazin.article.IColumnArticle,
                      host_restriction='xml')
class XMLArticle(XMLContent):

    @property
    def xml(self):
        xml = self.context.xml
        self._include_infoboxes(xml)
        self._include_liveblogs(xml)
        return xml

    def _include_infoboxes(self, xml):
        for infobox in xml.xpath('/article/body/division/infobox'):
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

    # who needs this?
    def _include_liveblogs(self, xml):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)

        for liveblog in xml.xpath('/article/body/division/liveblog'):
            blog_id = liveblog.get('blogID', '')
            version = liveblog.get('version', '')
            el = lxml.objectify.SubElement(
                liveblog, '{http://www.edge-delivery.org/esi/1.0}include',
                nsmap={'esi': 'http://www.edge-delivery.org/esi/1.0'})
            if version == '3':
                url = '{}/{}/index.html'.format(
                    conf.get('liveblog_backend_url_v3', ''), blog_id)
            else:
                url = '{}/{}.html'.format(
                    conf.get('liveblog_backend_url', ''), blog_id)
            el.set('src', url)
            liveblog.set('data-type', 'esi-content')
            liveblog.attrib.pop('blogID')
            liveblog.tag = 'div'


@zeit.web.view_config(context=zeit.content.cp.interfaces.ICenterPage,
                      host_restriction='xml')
@zeit.web.view_config(context=zeit.content.cp.interfaces.ICP2009,
                      host_restriction='xml')
@zeit.web.view_config(context=zeit.content.cp.interfaces.ICP2015,
                      host_restriction='xml')
class XMLCenterpage(XMLContent):

    @property
    def xml(self):
        return zeit.content.cp.interfaces.IRenderedXML(self.context)
