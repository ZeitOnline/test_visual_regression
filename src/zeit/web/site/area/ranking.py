import logging
import math

import pyramid
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
    'authors',
    'date-last-modified',
    'date_first_released',
    'date_last_published',
    'image-base-id',
    'last-semantic-change',
    'lead_candidate'
    'product_id',
    'serie',
    'supertitle',
    'teaser_text',
    'title',
    'type',
    'uniqueId'
])


FIELD_MAP = [
    (u'authors', u'authorships'),
    (u'supertitle', u'teaserSupertitle'),
    (u'teaser_text', u'teaserText'),
    (u'title', u'teaserTitle')
]


DATE_MAP = [
    (u'date-last-modified', u'date_last_modified'),
    (u'date_first_released', u'date_first_released'),
    (u'last-semantic-change', u'last_semantic_change'),
    (u'date_last_published', u'date_last_published'),
    (u'date_last_published', u'date_last_published_semantic')
]


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

    raw_query = zeit.cms.content.property.ObjectPathProperty(
        '.raw_query', IRanking['raw_query'])

    _page = zeit.cms.content.property.ObjectPathProperty(
        '.page', IRanking['page'])

    _hits = zeit.cms.content.property.ObjectPathProperty(
        '.hits', IRanking['hits'])

    def _query_solr(self, query, sort_order):
        result = []
        conn = zope.component.getUtility(zeit.solr.interfaces.ISolr)
        start = self._v_retrieved_content + self.count * (self.page - 1)
        try:
            with zeit.web.core.metrics.timer('solr.reponse_time'):
                solr_result = conn.search(
                    query,
                    sort=sort_order,
                    rows=self.count_to_replace_duplicates,
                    start=start,
                    fl=FIELDS)
        except (pysolr.SolrError, ValueError) as e:
            log.warning(u'{} for query {}'.format(e, query))
        else:
            self.hits = solr_result.hits
            for doc in solr_result:
                doc = self.document_hook(doc)
                content = zeit.cms.interfaces.ICMSContent(doc, None)
                if content is not None:
                    result.append(content)
        return result

    @staticmethod
    def document_hook(doc):
        for source, target in FIELD_MAP:
            try:
                doc[target] = doc[source]
            except KeyError:
                continue

        for source, target in DATE_MAP:
            try:
                doc[target] = zc.iso8601.parse.datetimetz(str(doc[source]))
            except (KeyError, UnicodeEncodeError, ValueError):
                continue

        serie = doc.get('serie', None)
        source = zeit.cms.content.interfaces.ICommonMetadata['serie'].source
        doc['serie'] = source.factory.values.get(serie, None)

        # XXX The asset badges are not indexed in solr, so we lie about them
        doc['gallery'] = doc['video'] = doc['video_2'] = None

        return doc

    @property
    def query_string(self):
        request = pyramid.threadlocal.get_current_request()
        param = u' '.join(request.GET.getall('q'))
        if param and self.raw_query:
            return param

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
