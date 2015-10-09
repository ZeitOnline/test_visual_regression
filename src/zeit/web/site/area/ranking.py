import collections
import logging
import math

import pysolr
import zc.iso8601.parse
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
import zeit.web.core.date
import zeit.web.core.metrics
import zeit.web.core.template


log = logging.getLogger(__name__)


FIELDS = ' '.join([
    'date_last_published',
    'date_last_published_semantic',
    'date_first_released',
    'image-base-id',
    'last-semantic-change',
    'product_id',
    'serie',
    'supertitle',
    'title',
    'uniqueId',
    'teaser_text',
    'type'
])


FIELD_MAP = [
    (u'supertitle', u'teaserSupertitle'),
    (u'title', u'teaserTitle'),
    (u'teaser_text', u'teaserText'),
]


ORDERS = collections.defaultdict(
    lambda: 'last-semantic-change desc', {
        'relevanz': 'score desc',
        'aktuell': 'last-semantic-change desc',
        'publikation': 'date_last_published asc'}
)


class IRanking(zeit.content.cp.interfaces.IArea):

    sort_order = zope.schema.TextLine(
        title=u'Search result order', default=u'aktuell', required=False)

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
        query = self._build_query()
        try:
            with zeit.web.core.metrics.timer('solr.reponse_time'):
                solr_result = conn.search(
                    query,
                    sort=ORDERS[self.sort_order],
                    rows=self.count,
                    fl=FIELDS,
                    start=self.count * (self.page - 1))
        except (pysolr.SolrError, ValueError) as e:
            log.warning(u'{} for query {}'.format(e, query))
            return result
        docs = collections.deque(solr_result)
        self.hits = solr_result.hits
        for block in self.placeholder:
            if not zeit.content.cp.interfaces.IAutomaticTeaserBlock.providedBy(
                    block) or not len(docs):
                result.append(block)
                continue
            context = self.document_hook(docs.popleft())
            try:
                block.insert(0, zeit.cms.interfaces.ICMSContent(context))
            except TypeError:
                log.debug('Corrupted search result', context.get('uniqueId'))
                continue
            result.append(block)
        return result

    def _build_query(self):
        return self.raw_query

    def document_hook(self, doc):
        for source, target in FIELD_MAP:
            try:
                doc[target] = doc[source]
            except KeyError:
                continue

        lsp = doc.get('date_last_published_semantic')
        if lsp:
            try:
                doc['date_last_published_semantic'] = (
                    zc.iso8601.parse.datetimetz(lsp))
            except:
                doc['date_last_published_semantic'] = None
        else:
            doc['date_last_published_semantic'] = None
            first = doc.get('date_first_released')
            if first:
                try:
                    doc['date_first_released'] = (
                        zc.iso8601.parse.datetimetz(lsp))
                except:
                    doc['date_first_released'] = None
            else:
                doc['date_first_released'] = None

        serie = doc.get('serie')
        if serie:
            source = zeit.cms.content.interfaces.ICommonMetadata[
                'serie'].source.factory
            doc['serie'] = source.values.get(serie, serie)
        else:
            doc['serie'] = None

        # XXX The asset badges are not indexed in solr, so we lie about them
        doc['gallery'] = None
        doc['video'] = None
        doc['video_2'] = None

        return doc

    @property
    def placeholder(self):
        return iter(self.context.values())

    @property
    def hits(self):
        if self._hits is None:
            self.values()
        return self._hits or 0

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
        pagination = zeit.web.core.template.calculate_pagination(
            self.current_page, self.total_pages)
        return pagination if pagination is not None else []
