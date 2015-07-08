import collections
import logging
import math

import zope.component
import zope.schema

import zeit.cms.content.property
import zeit.content.cp.automatic
import zeit.content.cp.interfaces
import zeit.find.daterange
import zeit.find.search
import zeit.solr.interfaces

import zeit.web
import zeit.web.core.block
import zeit.web.core.template


log = logging.getLogger(__name__)


FIELDS = ' '.join([
    'title',
    'uniqueId',
    'uuid'
])


HIGHLIGHTING = {
    'hl': 'true',
    'hl.fl': 'main_text,teaser_text',
    'hl.highlightMultiTerm': 'true',
    'hl.fragsize': '250',
    'hl.alternateField': 'teaser_text',
    'hl.snippets': '1',
    'hl.mergeContiguous': 'true',
    'hl.usePhraseHighlighter': 'true',
    'hl.simple.pre': '%3Cb%3E',
    'hl.simple.post': '%3C/b%3E'
}


ORDERS = collections.defaultdict(
    lambda: 'score desc', {
        'aktuell': 'last-semantic-change desc'}
)


class IRanking(zeit.content.cp.interfaces.IArea):

    sort_order = zope.schema.TextLine(
        title=u'Search result order', default=u'relevanz', required=False)

    raw_query = zope.schema.Text(
        title=u'Raw solr query', default=None, required=False)

    hits = zope.schema.Int(
        title=u'Search result count', default=None, required=False)

    page = zope.schema.Int(
        title=u'Search result page', default=None, required=False)


@zeit.web.register_area('ranking')
class Ranking(zeit.content.cp.automatic.AutomaticArea):

    zope.interface.implements(
        IRanking, zeit.content.cp.interfaces.IRenderedArea)

    sort_order = zeit.cms.content.property.ObjectPathProperty(
        '.sort_order', IRanking['sort_order'])

    query = zeit.cms.content.property.ObjectPathProperty(
        '.query', IRanking['query'])

    raw_query = zeit.cms.content.property.ObjectPathProperty(
        '.raw_query', IRanking['raw_query'])

    _page = zeit.cms.content.property.ObjectPathProperty(
        '.page', IRanking['page'])

    _hits = zeit.cms.content.property.ObjectPathProperty(
        '.hits', IRanking['hits'])

    def values(self):
        return self._values

    @zeit.web.reify
    def _values(self):
        result = []
        conn = zope.component.getUtility(zeit.solr.interfaces.ISolr)
        solr_result = conn.search(
            self.raw_query, sort=ORDERS[self.sort_order], rows=self.count,
            fl=FIELDS, start=self.count * (self.page - 1), **HIGHLIGHTING)
        docs = collections.deque(solr_result)
        self.hits = solr_result.hits
        for block in self.placeholder:
            if not zeit.content.cp.interfaces.IAutomaticTeaserBlock.providedBy(
                    block) or not len(docs):
                result.append(block)
                continue
            unique_id = docs.popleft().get('uniqueId')
            try:
                block.insert(0, zeit.cms.interfaces.ICMSContent(unique_id))
            except TypeError, err:
                log.debug('Corrupted search result', unique_id, err)
                continue
            result.append(block)
        return result

    @property
    def placeholder(self):
        return iter(self.context.values())

    @property
    def hits(self):
        if self._hits is None:
            self.values()
        return self._hits

    @hits.setter
    def hits(self, value):
        if self._hits is None:
            self._hits = value

    @property
    def page(self):
        if self._page is None:
            return 1
        return self._page

    @page.setter
    def page(self, value):
        self._page = value

    @zeit.web.reify
    def total_pages(self):
        if self.hits + self.count > 0:
            return int(math.ceil(float(self.hits) / float(self.count)))
        else:
            return 0

    @zeit.web.reify
    def current_page(self):
        return self.page

    @zeit.web.reify
    def pagination(self):
        return zeit.web.core.template.calculate_pagination(
            self.current_page, self.total_pages)
