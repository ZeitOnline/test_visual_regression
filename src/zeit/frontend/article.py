from grokcore.component import adapter, implementer
from zeit.frontend.block import IFrontendBlock
from zeit.magazin.interfaces import IArticleTemplateSettings
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
        try:
            block = IFrontendBlock(block, None)
            if block is not None:
                self.blocks.append(block)
        except OSError:
            log.error("Reference for %s does not exist." % type(block))


    def __iter__(self):
        return iter(self.blocks)


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
    return pages


class ILongformArticle(zeit.content.article.interfaces.IArticle):
    pass


@adapter(zeit.cms.repository.interfaces.IRepository)
@implementer(pyramid.interfaces.ITraverser)
class RepositoryTraverser(pyramid.traversal.ResourceTreeTraverser):

    def __call__(self, request):
        try:
            tdict = super(RepositoryTraverser, self).__call__(request)
            context = tdict['context']
            if zeit.content.article.interfaces.IArticle.providedBy(context):
                if IArticleTemplateSettings(context).template == 'longform':
                    zope.interface.alsoProvides(context, ILongformArticle)
            return self._change_viewname(tdict)
        except OSError, e:
            if e.errno == 2:
                raise pyramid.httpexceptions.HTTPNotFound()

    def _change_viewname(self, tdict):
        if tdict['view_name'][0:5] == 'seite' and not tdict['subpath']:
            tdict['view_name'] = 'seite'
        return tdict

