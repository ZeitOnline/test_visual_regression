from __future__ import absolute_import

import logging
import sys

import bugsnag
import gocept.lxml.objectify
import grokcore.component
import xml.sax.saxutils
import zc.sourcefactory.source
import zope.component
import zope.interface
import zope.security.proxy

from zeit.cms.checkout.interfaces import ILocalContent
import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.content.article.edit.interfaces
import zeit.content.article.interfaces
import zeit.retresco.interfaces

import zeit.web.core.application
import zeit.web.core.banner
import zeit.web.core.block
import zeit.web.core.interfaces
import zeit.web.core.jinja
import zeit.web.magazin.article


log = logging.getLogger(__name__)


class IColumnArticle(zeit.content.article.interfaces.IArticle):
    """Marker interface for articles that belong to a "column" series."""


class IFlexibleTOCArticle(zeit.content.article.interfaces.IArticle):
    """Marker interface for articles that contain a flexible table of
    contents.
    """


class IFAQArticle(zeit.content.article.interfaces.IArticle):
    """Marker interface for articles that contain a FAQ."""


class ILiveblogArticle(zeit.content.article.interfaces.IArticle):
    """Marker interface for articles that contain a liveblog."""


class ISeriesArticleWithFallbackImage(
        zeit.content.article.interfaces.IArticle):
    """Marker interface for articles that are part of a series with a
    fallback image.
    """


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
        wrapped = None
        try:
            wrapped = zeit.web.core.interfaces.IArticleModule(block, None)
        except:
            log.warn('Ignoring %s', block, exc_info=True)
            exc_info = sys.exc_info()
            path = zeit.web.core.jinja.get_current_request_path()
            bugsnag.notify(exc_info[1], traceback=exc_info[2], context=path)
            return
        if wrapped is not None:
            self.blocks.append(wrapped)


def _inject_banner_code(pages, pubtype):
    adconfig = {
        'zon': {
            'pages': range(1, len(pages) + 1),
            'ads': [{'tile': 3, 'paragraph': 1, 'type': 'mobile'},
                    {'tile': 8, 'paragraph': 1, 'type': 'desktop'},
                    {'tile': 4, 'paragraph': 4, 'type': 'mobile'},
                    {'tile': 4, 'paragraph': 4, 'type': 'desktop'}]
        },
        'longform': {
            'pages': [2],
            'ads': [{'tile': 7, 'paragraph': 5, 'type': 'desktop'}]
        }
    }

    # change place5 against ctm if configured
    toggles = zeit.web.core.application.FEATURE_TOGGLES
    place5 = ({'tile': 5, 'paragraph': 6, 'type': 'desktop'},
              {'tile': 'content_ad', 'paragraph': 6, 'type': ''},)
    if toggles.find('iqd_contentmarketing_ad'):
        adconfig['zon']['ads'].append(place5[1])
    else:
        adconfig['zon']['ads'].append(place5[0])

    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    p_length = conf.get('sufficient_paragraph_length', 10)

    for page_number, page in enumerate(pages, start=1):

        # (1) find everything which is a text-paragraph
        paragraphs = filter(lambda b: isinstance(
            b, zeit.web.core.block.Paragraph), page.blocks)

        # (1a) check if there is an editorial aside after paragraph 1
        if len(page.blocks) > 1 and not isinstance(
                page.blocks[1], zeit.web.core.block.Paragraph):
            adconfig['zon']['ads'][1] = {
                'tile': 8, 'paragraph': 2, 'type': 'desktop'}
            adconfig['longform']['ads'][0] = {
                'tile': 8, 'paragraph': 5, 'type': 'desktop'}

        # (2) get a list of those paragraphs, after which we can insert ads
        paragraphs = _paragraphs_by_length(
            paragraphs, sufficient_length=p_length)

        # (3a) Match ads to the cloned list of long paragraphs
        for index, paragraph in enumerate(paragraphs, start=1):
            try:
                ads = [ad for ad in adconfig[pubtype]['ads'] if ad[
                    'paragraph'] == index and page_number in adconfig[
                    pubtype]['pages']]
            except IndexError:
                continue
            if ads is not None:
                # (3b) Insert the ad into the real page blocks
                for i, block in enumerate(page.blocks, start=1):
                    if paragraph == block:
                        for ad in ads:
                            if ad['tile'] == 'content_ad':
                                adplace = zeit.web.core.banner.ContentAdBlock(
                                    "iq-artikelanker")
                            else:
                                adplace = zeit.web.core.banner.Place(
                                    ad['tile'], ad[
                                        'type'], on_page_nr=page_number)
                            # do not place ad after last paragraph
                            if i < len(page.blocks):
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


@grokcore.component.adapter(zeit.content.article.interfaces.IArticle)
@grokcore.component.implementer(
    zeit.content.article.edit.interfaces.IEditableBody)
def get_retresco_body(article):
    # We want to be very cautious here and retreat to static XML as a
    # source for our article body if anything goes wrong/ takes too long
    # with the TMS body.
    xml = zope.security.proxy.removeSecurityProxy(article.xml['body'])
    toggles = zeit.web.core.application.FEATURE_TOGGLES
    seo = zeit.seo.interfaces.ISEO(article)

    if (toggles.find('enable_intext_links') and
            not ILocalContent.providedBy(article) and
            not seo.disable_intext_links and
            not suppress_intextlinks(article)):
        if hasattr(article, '_v_retresco_body'):
            xml = article._v_retresco_body
        else:
            conf = zope.component.getUtility(
                zeit.web.core.interfaces.ISettings)
            tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
            try:
                body = tms.get_article_body(
                    article, timeout=conf.get('retresco_timeout', 0.1))
                xml = gocept.lxml.objectify.fromstring(body)
            except Exception:
                log.warning(
                    'Retresco body failed for %s', article.uniqueId,
                    exc_info=True)
            else:
                article._v_retresco_body = xml
    elif zeit.retresco.interfaces.ITMSContent.providedBy(article):
        # While this branch is quite correct, it is mostly a fallback for tests
        content = zeit.cms.interfaces.ICMSContent(article.uniqueId, None)
        if zeit.content.article.interfaces.IArticle.providedBy(content):
            xml = content.xml.body

    return zope.component.queryMultiAdapter(
        (article, xml),
        zeit.content.article.edit.interfaces.IEditableBody)


class ValuesCachingEditableBody(zeit.content.article.edit.body.EditableBody):

    def values(self):
        if zeit.cms.checkout.interfaces.ILocalContent.providedBy(
                self.__parent__):
            return super(ValuesCachingEditableBody, self).values()
        self.ensure_division()  # Old articles don't always have divisions.
        if not hasattr(self.__parent__, '_v_body_values'):
            self.__parent__._v_body_values = super(
                ValuesCachingEditableBody, self).values()
        # Return a copy, as e.g. pages_of_article below deletes modules from it
        return self.__parent__._v_body_values[:]


def pages_of_article(article, advertising_enabled=True):
    body = zeit.content.article.edit.interfaces.IEditableBody(article)
    # Call values() first, to ensure that ensure_divsion() was called.
    blocks = body.values()

    # IEditableBody excludes the first division since it cannot be edited
    first_division = body.xml.xpath('division[@type="page"]')[0]
    first_division = body._get_element_for_node(first_division)

    pages = []
    page = Page(first_division)
    pages.append(page)

    try:
        if blocks[0] == article.header.module:
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

    if zeit.web.magazin.article.ILongformArticle.providedBy(article):
        pubtype = 'longform'
    else:
        pubtype = 'zon'

    return _inject_banner_code(pages, pubtype)


@zope.interface.implementer(zeit.web.core.interfaces.IArticleModule)
class FAQItemBlock(Page):

    """A block for FAQs, wrapped around questions and corresponding answers.
    This may be placed in z.w.c.block instead, but will result in
    circular imports.
    """

    def __init__(self):
        self.blocks = []


def restructure_faq_article(page):
    # FAQs by definition consist only of a single page.
    restructured_blocks = []
    for block in page.blocks:
        try:
            previous_block = restructured_blocks[-1]
        except IndexError:
            previous_block = None

        if isinstance(block, zeit.web.core.block.Intertitle):
            # Handle intertitles, representing a FAQ question.
            faq_item_block = FAQItemBlock()
            faq_item_block.append(block)
            restructured_blocks.append(faq_item_block)
        elif zeit.web.core.interfaces.IContentAdBlock.providedBy(block):
            # Ad blocks should never be part of an answer.
            restructured_blocks.append(block)
        elif isinstance(previous_block, FAQItemBlock):
            # Add further blocks as answers to their corresponding question.
            previous_block.append(block)
        else:
            # Everything else is just a regular block (e.g. paragraphs that
            # appear before the first intertitle question).
            restructured_blocks.append(block)
        page.blocks = restructured_blocks
    return page


def convert_authors(article):
    is_longform = zeit.web.magazin.article.ILongformArticle.providedBy(article)
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


@grokcore.component.adapter(zeit.web.core.interfaces.INextread)
@grokcore.component.implementer(zeit.content.image.interfaces.IImages)
def images_from_nextread(context):
    if not len(context):
        raise zope.component.interfaces.ComponentLookupError(
            'Could not adapt', context, zeit.content.image.interfaces.IImages)
    else:
        return zeit.content.image.interfaces.IImages(context[0], None)


class RessortFolderSource(zeit.cms.content.sources.SimpleXMLSourceBase):

    product_configuration = (
        zeit.cms.content.sources.SubRessortSource.product_configuration)
    config_url = zeit.cms.content.sources.SubRessortSource.config_url

    master_node_xpath = (
        zeit.cms.content.sources.SubRessortSource.master_node_xpath)
    slave_tag = zeit.cms.content.sources.SubRessortSource.slave_tag
    attribute = zeit.cms.content.sources.SubRessortSource.attribute

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
    parts = [cms_content_type(context), 'article']
    if zeit.web.core.view.is_advertorial(context, None):
        parts[1] = 'advertorial'
    elif getattr(context, 'serie', None):
        parts[1] = 'serie'
        if context.serie.column:
            parts[1] = 'column'
    if getattr(context, 'genre', None):
        parts.append(context.genre)
    return '.'.join(parts)


@grokcore.component.adapter(zeit.content.article.interfaces.IArticle)
@grokcore.component.implementer(zeit.web.core.interfaces.ILiveblogInfo)
class LiveblogInfo(object):

    def __init__(self, context):
        self.context = context

    @zeit.web.reify
    def liveblog(self):
        for block in self.context.body.values():
            if zeit.content.article.edit.interfaces.ILiveblog.providedBy(
                    block):
                return zeit.web.core.interfaces.IArticleModule(block)

    @property
    def is_live(self):
        if self.liveblog:
            return self.liveblog.is_live

    @property
    def last_modified(self):
        if self.liveblog:
            return self.liveblog.last_modified

    @property
    def collapse_preceding_content(self):
        if self.liveblog:
            return self.liveblog.collapse_preceding_content

    @property
    def has_relative_dates(self):
        if self.liveblog:
            theme = self.liveblog.get_amp_themed_id(self.liveblog.id)
            if theme:
                return theme.startswith('zon-amp-solo')


TEMPLATE_INTERFACES = {
    'faq': (IFAQArticle,),
    'flexible-toc': (IFlexibleTOCArticle,),
    'zon-liveblog': (ILiveblogArticle,),
    # Should we check that the article provides IZMOContent? Because those
    # templates are only available there.
    'longform': (zeit.web.magazin.article.ILongformArticle,),
    'short': (zeit.web.magazin.article.IShortformArticle,),
    # XXX Somewhat confusing compared to core.IColumnArticle
    'column': (zeit.web.magazin.article.IColumnArticle,),
    'photocluster': (zeit.web.magazin.article.IPhotoclusterArticle,),
}


@grokcore.component.adapter(
    zeit.content.article.interfaces.IArticle, name='template')
@grokcore.component.implementer(
    zeit.web.core.interfaces.IContentMarkerInterfaces)
def mark_according_to_template(context):
    return TEMPLATE_INTERFACES.get(context.template)


@grokcore.component.adapter(
    zeit.content.article.interfaces.IArticle, name='serie')
@grokcore.component.implementer(
    zeit.web.core.interfaces.IContentMarkerInterfaces)
def mark_according_to_series(context):
    if not context.serie:
        return None
    result = []
    if context.serie.column:
        result.append(IColumnArticle)
    if context.serie.fallback_image:
        result.append(ISeriesArticleWithFallbackImage)
    return result


def get_keywords(context):
    if zeit.web.core.application.FEATURE_TOGGLES.find('keywords_from_tms'):
        conf = zope.component.getUtility(
            zeit.web.core.interfaces.ISettings)
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        try:
            timeout = conf.get('retresco_timeout', 0.1)
            return tms.get_article_keywords(context, timeout=timeout)
        except Exception:
            log.warning(
                'Retresco keywords failed for %s', context.uniqueId,
                exc_info=True)
            # Fall back to the vivi-stored keywords, i.e. without any links
            # since only the TMS knows about those.
            if not hasattr(context, 'keywords'):
                return []
            result = []
            for keyword in context.keywords:
                if not keyword.label:
                    continue
                keyword.link = None
                result.append(keyword)
            return result
    else:
        if not hasattr(context, 'keywords'):
            return []
        result = []
        for keyword in context.keywords:
            if not keyword.label:
                continue
            if not keyword.url_value:
                uuid = keyword.uniqueId.replace('tag://', '')
                keyword = zope.component.getUtility(
                    zeit.cms.tagging.interfaces.IWhitelist).get(uuid)
                if keyword is None:
                    continue
            if keyword.url_value:
                keyword.link = u'thema/{}'.format(keyword.url_value)
            else:
                keyword.link = None
            result.append(keyword)
        return result


class IntextlinkBlacklistSource(zeit.cms.content.sources.XMLSource):
    # Only contextual so we can customize source_class

    product_configuration = 'zeit.web'
    config_url = 'intextlink-blacklist-url'

    class source_class(zc.sourcefactory.source.FactoredContextualSource):

        def __contains__(self, value):
            return value in self.factory

    # This is the one case where the zc.sourcefactory abstractions are rather
    # unhelpful: we don't want to enumerate the values, but do a targeted
    # "contains" check instead.
    def __contains__(self, x):
        return bool(self._get_tree().xpath(
            '//entity[@type="%s" and text()="%s"]' % (x.entity_type, x.label)))


INTEXTLINK_BLACKLIST = IntextlinkBlacklistSource()(None)


def suppress_intextlinks(article):
    for keyword in get_keywords(article):
        if keyword in INTEXTLINK_BLACKLIST:
            return True
    return False
