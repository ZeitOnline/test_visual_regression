import logging

import gocept.lxml.objectify
import grokcore.component
import xml.sax.saxutils
import zope.component
import zope.interface
import zope.security.proxy

import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.connector.cache
import zeit.content.article.article
import zeit.content.article.edit.body
import zeit.content.article.edit.interfaces
import zeit.content.article.interfaces
import zeit.retresco.interfaces

import zeit.web.core.application
import zeit.web.core.banner
import zeit.web.core.block
import zeit.web.core.interfaces
import zeit.web.core.template


log = logging.getLogger(__name__)


@zope.interface.implementer(zeit.web.core.interfaces.IPage)
class Page(object):

    def __init__(self, division):
        self.number = division.number
        self.teaser = division.teaser or ''
        self.blocks = []

    def __iter__(self):
        return iter(self.blocks)

    def __len__(self):
        return len(self.blocks)

    def __getitem__(self, key):
        return self.blocks[key]

    def __setitem__(self, key, value):
        self.blocks[key] = value

    def __delitem__(self, key):
        del self.blocks[key]

    def append(self, block):
        block = zeit.web.core.interfaces.IFrontendBlock(block, None)
        if block is not None:
            self.blocks.append(block)


def _inject_banner_code(pages, pubtype):
    adconfig = {
        'zon': {
            'pages': range(1, len(pages) + 1),
            'ads': [{'tile': 7, 'paragraph': 2, 'type': 'desktop'},
                    {'tile': 4, 'paragraph': 4, 'type': 'mobile'},
                    {'tile': 'content_ad', 'paragraph': 6, 'type': ''}]
        },
        'longform': {
            'pages': [2],
            'ads': [{'tile': 7, 'paragraph': 5, 'type': 'desktop'}]
        }
    }

    toggles = zeit.web.core.application.FEATURE_TOGGLES
    if toggles.find('iqd_mobile_transition_article'):
        # temporary append ad tile here
        # put into config if toggle is deleted
        place = {'tile': 3, 'paragraph': 1, 'type': 'mobile'}
        adconfig['zon']['ads'].append(place)

    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    p_length = conf.get('sufficient_paragraph_length', 10)

    for page_number, page in enumerate(pages, start=1):
        paragraphs = filter(lambda b: isinstance(
            b, zeit.web.core.block.Paragraph), page.blocks)
        paragraphs = _paragraphs_by_length(
            paragraphs, sufficient_length=p_length)

        for index, paragraph in enumerate(paragraphs, start=1):
            try:
                ad = [ad for ad in adconfig[pubtype]['ads'] if ad[
                    'paragraph'] == index and page_number in adconfig[
                    pubtype]['pages']][0]
            except IndexError:
                continue
            if ad is not None:
                for i, block in enumerate(page.blocks, start=1):
                    if paragraph == block:
                        if ad['tile'] == 'content_ad':
                            adplace = zeit.web.core.banner.ContentAdBlock(
                                "iq-artikelanker")
                        else:
                            adplace = zeit.web.core.banner.Place(
                                ad['tile'], ad['type'], on_page_nr=page_number)
                        # do not place ad after last paragraph
                        if i < len(page.blocks) - 1:
                            page.blocks.insert(i, adplace)

    return pages


def _paragraphs_by_length(paragraphs, sufficient_length=10):
    previous_length = 0
    filtered_paragraphs = []
    for p in paragraphs:
        if len(p) + previous_length <= sufficient_length:
            previous_length = len(p) + previous_length
        else:
            filtered_paragraphs.append(p)
            previous_length = 0
    return filtered_paragraphs


@zope.component.adapter(zeit.content.article.interfaces.IArticle)
@zope.interface.implementer(zeit.content.article.edit.interfaces.IEditableBody)
def get_retresco_body(article):
    # We want to be very cautious here and retreat to static XML as a
    # source for our article body if anything goes wrong/ takes too long
    # with the TMS body.

    xml = zope.security.proxy.removeSecurityProxy(article.xml['body'])

    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    conn = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
    toggles = zeit.web.core.application.FEATURE_TOGGLES

    if toggles.find('enable_intext_links'):
        try:
            assert not zeit.seo.interfaces.ISEO(article).disable_intext_links

            uuid = zeit.cms.content.interfaces.IUUID(article).id
            timeout = conf.get('retresco_timeout', 0.1)
            body = conn.get_article_body(uuid, timeout=timeout)

            if unichr(65533) in body:
                # XXX Stopgap until tms encoding issues are resolved
                raise ValueError(
                    'Encountered encoding issues in retresco body')

            xml = gocept.lxml.objectify.fromstring(body)
        except AssertionError:
            log.debug('Retresco body disabled for %s', article.uniqueId)
        except:
            log.warning(
                'Retresco body failed for %s', article.uniqueId, exc_info=True)

    return zope.component.queryMultiAdapter(
        (article, xml),
        zeit.content.article.edit.interfaces.IEditableBody)


def pages_of_article(article, advertising_enabled=True):
    body = zope.component.getAdapter(
        article,
        zeit.content.article.edit.interfaces.IEditableBody,
        name='retresco')
    body.ensure_division()  # Old articles don't always have divisions.

    # IEditableBody excludes the first division since it cannot be edited
    first_division = body.xml.xpath('division[@type="page"]')[0]
    first_division = body._get_element_for_node(first_division)

    pages = []
    page = Page(first_division)
    pages.append(page)
    blocks = body.values()

    header = zeit.content.article.edit.interfaces.IHeaderArea(article)
    try:
        if blocks[0] == header.module:
            del blocks[0]
    except IndexError:
        pass
    for block in blocks:
        if zeit.content.article.edit.interfaces.IDivision.providedBy(block):
            page = Page(block)
            pages.append(page)
        else:
            page.append(block)

    if advertising_enabled is False:
        return pages

    if zeit.web.core.article.ILongformArticle.providedBy(article):
        pubtype = 'longform'
    else:
        pubtype = 'zon'

    return _inject_banner_code(pages, pubtype)


def convert_authors(article):
    is_longform = zeit.web.core.article.ILongformArticle.providedBy(article)
    author_list = []
    try:
        author_ref = article.authorships
        for index, author in enumerate(author_ref):
            location = zeit.content.author.interfaces.IAuthorReference(
                author).location
            author = {
                'name': getattr(author.target, 'display_name', None),
                'href': getattr(author.target, 'uniqueId', None),
                'prefix': u'', 'suffix': u'', 'location': u''}
            # add location
            if location and not is_longform:
                author['location'] = u', {}'.format(location)
            # add prefix
            if index == 0:
                if is_longform:
                    author['prefix'] = u'\u2014 von'
                else:
                    author['prefix'] = u' von'
            # add suffix
            if index == len(author_ref) - 2:
                author['suffix'] = u' und'
            elif index < len(author_ref) - 1:
                author['suffix'] = u', '
            author_list.append(author)
        return author_list
    except (IndexError, OSError):
        return []


class ILongformArticle(zeit.content.article.interfaces.IArticle):
    # TODO: Please remove when we have Longforms for ICMSContent
    pass


class IFeatureLongform(ILongformArticle):
    pass


class IShortformArticle(zeit.content.article.interfaces.IArticle):
    pass


class IColumnArticle(zeit.content.article.interfaces.IArticle):
    pass


class ILiveblogArticle(zeit.content.article.interfaces.IArticle):
    pass


class IPhotoclusterArticle(zeit.content.article.interfaces.IArticle):
    pass


@grokcore.component.adapter(zeit.web.core.interfaces.INextread)
@grokcore.component.implementer(zeit.content.image.interfaces.IImages)
def images_from_nextread(context):
    if not len(context):
        raise zope.component.interfaces.ComponentLookupError(
            'Could not adapt', context, zeit.content.image.interfaces.IImages)
    else:
        return zeit.content.image.interfaces.IImages(context[0])


class RessortFolderSource(zeit.cms.content.sources.SimpleXMLSourceBase):

    product_configuration = (
        zeit.cms.content.sources.SubNavigationSource.product_configuration)
    config_url = zeit.cms.content.sources.SubNavigationSource.config_url

    master_node_xpath = (
        zeit.cms.content.sources.SubNavigationSource.master_node_xpath)
    slave_tag = zeit.cms.content.sources.SubNavigationSource.slave_tag
    attribute = zeit.cms.content.sources.SubNavigationSource.attribute

    # Same idea as zeit.cms.content.sources.MasterSlavesource.getTitle()
    def find(self, ressort, subressort):
        tree = self._get_tree()
        if not subressort:
            nodes = tree.xpath(
                u'{master_node_xpath}[@{attribute} = {master}]'.format(
                    master_node_xpath=self.master_node_xpath,
                    attribute=self.attribute,
                    master=xml.sax.saxutils.quoteattr(ressort)))
        else:
            nodes = tree.xpath(
                u'{master_node_xpath}[@{attribute} = {master}]'
                u'/{slave_tag}[@{attribute} = {slave}]'.format(
                    master_node_xpath=self.master_node_xpath,
                    attribute=self.attribute,
                    slave_tag=self.slave_tag,
                    master=xml.sax.saxutils.quoteattr(ressort),
                    slave=xml.sax.saxutils.quoteattr(subressort)))
        if not nodes:
            return {}
        return zeit.cms.interfaces.ICMSContent(
            nodes[0].get('uniqueId'), {})

RESSORTFOLDER_SOURCE = RessortFolderSource()


@grokcore.component.adapter(zeit.cms.interfaces.ICMSContent)
@grokcore.component.implementer(zeit.web.core.interfaces.IDetailedContentType)
def cms_content_type(context):
    typ = zeit.cms.interfaces.ITypeDeclaration(context, None)
    if typ is None:
        return 'unknown'
    return typ.type_identifier


@grokcore.component.adapter(zeit.content.article.interfaces.IArticle)
@grokcore.component.implementer(zeit.web.core.interfaces.IDetailedContentType)
def content_type(context):
    typ = cms_content_type(context)
    subtyp = 'article'
    if zeit.web.core.view.is_advertorial(context, None):
        subtyp = 'advertorial'
    elif getattr(context, 'serie', None):
        subtyp = "serie"
        if context.serie.column:
            subtyp = "column"
    return '{}.{}'.format(typ, subtyp)


@grokcore.component.adapter(zeit.content.article.interfaces.IArticle)
@grokcore.component.implementer(zeit.web.core.interfaces.ILiveblogInfo)
class LiveblogInfo(object):

    def __init__(self, context):
        self.context = context

    @zeit.web.reify
    def liveblog(self):
        body = zeit.content.article.edit.interfaces.IEditableBody(self.context)
        for block in body.values():
            if zeit.content.article.edit.interfaces.ILiveblog.providedBy(
                    block):
                return zeit.web.core.interfaces.IFrontendBlock(block)

    @property
    def is_live(self):
        if self.context.header_layout == 'liveblog-closed':
            return False
        elif self.liveblog:
            return self.liveblog.is_live

    @property
    def is_slow(self):
        if self.liveblog:
            return (self.liveblog.is_live and
                    self.context.header_layout == 'liveblog-closed')

    @property
    def last_modified(self):
        if self.liveblog:
            return self.liveblog.last_modified
