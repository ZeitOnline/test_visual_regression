from grokcore.component import adapter, implementer
from zeit.frontend.block import IFrontendBlock
import logging
import pyramid.interfaces
import pyramid.traversal
import zeit.cms.repository.interfaces
import zeit.content.article
import zeit.content.article.article
import zeit.content.article.edit.interfaces
import zeit.content.article.interfaces
import zeit.frontend.interfaces
import zope.interface
import pyramid.httpexceptions
import zeit.content.article.interfaces


log = logging.getLogger(__name__)


@zope.interface.implementer(zeit.frontend.interfaces.IPage)
class Page(object):

    def __init__(self, division):
        self.number = division.number
        self.teaser = division.teaser or ''
        self.blocks = []

    def append(self, block):
        block = IFrontendBlock(block, None)
        if block is not None:
            self.blocks.append(block)

    def __iter__(self):
        return iter(self.blocks)

##
#
# Injecting banner code in page.blocks
# counts and injects only after paragraphs (2nd actually)
# tile 7 and 8 are injected
#
##
def _inject_banner_code(pages, advertising_enabled):
    _tile_list = [7, 8]  # banner tiles in articles
    _possible_paragraphs = [2, 6]  # paragraph(s) to insert ad after

    if(advertising_enabled):
        for page in pages:
            for index, pp in enumerate(_possible_paragraphs):
                paragraphs = filter(
                    lambda b: isinstance(
                        b, zeit.frontend.block.Paragraph), page.blocks)
                if len(paragraphs) > pp + 1:
                    try:
                        _para = paragraphs[pp]
                        for i, block in enumerate(page.blocks):
                            if _para == block:
                                t = _tile_list[index] - 1
                                page.blocks.insert(
                                    i, zeit.frontend.banner.banner_list[t])
                                break
                    except IndexError:
                        pass
    return pages


@adapter(zeit.content.article.interfaces.IArticle)
@implementer(zeit.frontend.interfaces.IPages)
def pages_of_article(context):
    body = zeit.content.article.edit.interfaces.IEditableBody(context)
    try:
        advertising_enabled = context.advertising_enabled
    except AttributeError:
        advertising_enabled = True
    # IEditableBody excludes the first division since it cannot be edited
    first_division = body.xml.xpath('division[@type="page"]')[0]
    first_division = body._get_element_for_node(first_division)

    pages = []
    page = Page(first_division)
    pages.append(page)
    for block in body.values():
        if zeit.content.article.edit.interfaces.IDivision.providedBy(block):
            page = Page(block)
            pages.append(page)
        else:
            page.append(block)
    return _inject_banner_code(pages, advertising_enabled)


class ILongformArticle(zeit.content.article.interfaces.IArticle):
    pass


class IShortformArticle(zeit.content.article.interfaces.IArticle):
    pass


class IColumnArticle(zeit.content.article.interfaces.IArticle):
    pass
