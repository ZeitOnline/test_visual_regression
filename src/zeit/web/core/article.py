import grokcore.component
import zope.interface

import zeit.cms.repository.interfaces
import zeit.content.article
import zeit.content.article.article
import zeit.content.article.edit.interfaces
import zeit.content.article.interfaces

import zeit.web.core.block
import zeit.web.core.centerpage
import zeit.web.core.interfaces


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
        block = zeit.web.core.block.IFrontendBlock(block, None)
        if block is not None:
            self.blocks.append(block)


def _inject_banner_code(
        pages, advertising_enabled, is_longform, pubtype='zon'):
    """Injecting banner code in page.blocks counts and injects only after
    paragraphs, configured for zon, zmo, longforms... for now"""

    possible_pages = [i for i in xrange(1, len(pages) + 1)]
    banner_conf = {
        'zon': {
            'tiles': [7],  # banner tiles in articles
            'ad_paras': [2],  # paragraph(s) to insert ad after
            'content_ad_para': [4]  # paragraph/s to insert content ad after
        },
        'zmo': {
            'tiles': [7, 8],
            'ad_paras': [2, 6],
            'content_ad_para': [4]
        },
        'longform': {
            'tiles': [8],
            'ad_paras': [5]
        }
    }

    if is_longform:
        possible_pages = [2]  # page 1 is somehow the "intro text"
        pubtype = 'longform'

    if advertising_enabled:
        for i, page in enumerate(pages, start=1):
            if i in possible_pages:
                _place_adtag_by_paragraph(page,
                                          banner_conf[pubtype]['tiles'],
                                          banner_conf[pubtype]['ad_paras'])
                if not is_longform:
                    _place_content_ad_by_paragraph(
                        page, banner_conf[pubtype]['content_ad_para'])
    return pages


def _place_adtag_by_paragraph(page, tile_list, possible_paragraphs):
    paragraphs = filter(
        lambda b: isinstance(b, zeit.web.core.block.Paragraph), page.blocks)

    for index, pp in enumerate(possible_paragraphs):
        if len(paragraphs) > pp + 1:
            try:
                _para = paragraphs[pp]
                for i, block in enumerate(page.blocks):
                    if _para == block:
                        t = tile_list[index] - 1
                        page.blocks.insert(
                            i, zeit.web.core.banner.banner_list[t])
                        break
            except IndexError:
                pass


def _place_content_ad_by_paragraph(page, possible_paragraphs):
    paragraphs = filter(
        lambda b: isinstance(b, zeit.web.core.block.Paragraph), page.blocks)
    contentAd = zeit.web.core.banner.ContentAdBlock("iq-artikelanker")

    for index, pp in enumerate(possible_paragraphs):
        if len(paragraphs) > pp + 1:
            try:
                _para = paragraphs[pp]
                for i, block in enumerate(page.blocks):
                    if _para == block:
                        page.blocks.insert(i, contentAd)
                        break
            except IndexError:
                pass


@grokcore.component.adapter(zeit.content.article.interfaces.IArticle)
@grokcore.component.implementer(zeit.web.core.interfaces.IPages)
def pages_of_article(context):
    body = zeit.content.article.edit.interfaces.IEditableBody(context)
    try:
        advertising_enabled = context.advertising_enabled
    except AttributeError:
        advertising_enabled = True
    try:
        is_longform = context.is_longform
    except AttributeError:
        is_longform = False
    # IEditableBody excludes the first division since it cannot be edited
    first_division = body.xml.xpath('division[@type="page"]')[0]
    first_division = body._get_element_for_node(first_division)

    pages = []
    page = Page(first_division)
    pages.append(page)
    blocks = body.values()
    # delete article image. it resides in its own property 'main_image_block'
    if zeit.content.article.edit.interfaces.IImage.providedBy(blocks[0]):
        del blocks[0]
    for block in blocks:
        if zeit.content.article.edit.interfaces.IDivision.providedBy(block):
            page = Page(block)
            pages.append(page)
        else:
            page.append(block)
    if zeit.magazin.interfaces.IZMOContent.providedBy(context):
        return _inject_banner_code(
            pages, advertising_enabled, is_longform, pubtype='zmo')
    return _inject_banner_code(pages, advertising_enabled, is_longform)


class ILongformArticle(zeit.content.article.interfaces.IArticle):
    # TODO: Please remove when we have Longforms for ICMSContent
    pass


class IFeatureLongform(zeit.content.article.interfaces.IArticle):
    pass


class IShortformArticle(zeit.content.article.interfaces.IArticle):
    pass


class IColumnArticle(zeit.content.article.interfaces.IArticle):
    pass


class ILiveblogArticle(zeit.content.article.interfaces.IArticle):
    pass


class IPhotoclusterArticle(zeit.content.article.interfaces.IArticle):
    pass


@grokcore.component.implementer(zeit.web.core.interfaces.ITeaserSequence)
@grokcore.component.adapter(zeit.web.core.interfaces.INextreadTeaserBlock)
class NextreadTeaserBlock(zeit.web.core.centerpage.TeaserBlock):
    pass
