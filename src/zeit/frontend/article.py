from zeit.frontend.block import IFrontendBlock
import zeit.content.article.edit.interfaces
import zeit.content.article.interfaces
import zeit.frontend.interfaces
import zope.component


class Page(object):

    zope.interface.implements(zeit.frontend.interfaces.IPage)

    def __init__(self, division):
        self.number = division.number
        self.teaser = division.teaser
        self.blocks = []

    def append(self, block):
        self.blocks.append(IFrontendBlock(block))

    def __iter__(self):
        return iter(self.blocks)


@zope.component.adapter(zeit.content.article.interfaces.IArticle)
@zope.interface.implementer(zeit.frontend.interfaces.IPages)
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
    return pages


def configure_components():
    zope.component.provideAdapter(pages_of_article)
