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


def _inject_banner_code(pages):
    _tile = 4 # banner tile in articles
    _p = 3 # paragraph to insert ad before
    for index, page in enumerate(pages, start=1):
        if index % 2 != 0 and len(page.blocks) > 2:
            page.blocks.insert(_p, zeit.frontend.banner.banner_list[_tile-1])
    return pages


@adapter(zeit.content.article.interfaces.IArticle)
@implementer(zeit.frontend.interfaces.IPages)
def pages_of_article(context):
    body = zeit.content.article.edit.interfaces.IEditableBody(context)
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
    return _inject_banner_code(pages)


class ILongformArticle(zeit.content.article.interfaces.IArticle):
    pass


class IShortformArticle(zeit.content.article.interfaces.IArticle):
    pass
