import logging
import math

import pyramid
import pysolr
import zc.iso8601.parse
import zope.component
import zope.schema

from zeit.solr import query as lq
import zeit.cms.content.property
import zeit.content.cp.automatic
import zeit.content.cp.interfaces
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


@zeit.web.register_area('ranking')
class Ranking(zeit.content.cp.automatic.AutomaticArea):

    zope.interface.implements(
        IRanking, zeit.content.cp.interfaces.IRenderedArea)

    sort_order = zeit.cms.content.property.ObjectPathProperty(
        '.sort_order', IRanking['sort_order'])

    raw_query = zeit.cms.content.property.ObjectPathProperty(
        '.raw_query', IRanking['raw_query'])

    _hits = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'hits', IRanking['hits'])

    _hide_dupes = zeit.content.cp.area.Area.hide_dupes

    def __init__(self, context):
        super(Ranking, self).__init__(context)
        self.request = pyramid.threadlocal.get_current_request()

    @property
    def hide_dupes(self):
        """We pack our own deduping for solr queries, so we pretend hide_dupes
        to be False in that case, so that _extract_newest() doesn't try to
        dedupe results a second time.

        XXX If the solr deduping works out, move to zeit.content.cp?
        """
        if self.automatic_type == 'query':
            return False
        return self._hide_dupes

    def _query_solr(self, query, sort_order):
        if self._v_retrieved_content > 0:
            return []

        result = []
        conn = zope.component.getUtility(zeit.solr.interfaces.ISolr)
        try:
            with zeit.web.core.metrics.timer('solr.reponse_time'):
                solr_result = conn.search(
                    query,
                    sort=sort_order,
                    rows=self.count,
                    start=self.start,
                    fl=FIELDS,
                    fq=self.filter_query)
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

    @zeit.web.reify('default-term')
    def uids_above(self):
        if not self._hide_dupes:
            return zeit.web.dont_cache([])
        cp = zeit.content.cp.interfaces.ICenterPage(self)
        return [i.uniqueId for i in cp._teasered_content_above(self)
                if hasattr(i, 'uniqueId')]

    @zeit.web.reify
    def filter_query(self):
        if len(self.uids_above) == 0:
            return lq.any_value()
        return lq.not_(lq.or_(
            *[lq.field_raw('uniqueId', i) for i in self.uids_above]))

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

        doc.setdefault('lead_candidate', False)

        return doc

    @zeit.web.reify
    def query_string(self):
        param = u' '.join(self.request.GET.getall('q'))
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

    @zeit.web.reify
    def start(self):
        return self.count * max(self.page - 1 - (len(self.uids_above) > 0), 0)

    @zeit.web.reify
    def count(self):
        if self.page == 1 and len(self.uids_above) > 0:
            return 0
        return self._count

    @zeit.web.reify
    def page(self):
        try:
            return abs(int(self.request.GET['p']))
        except (KeyError, TypeError, ValueError):
            return 1

    @zeit.web.reify
    def current_page(self):
        return self.page  # Compat to article pagination

    @zeit.web.reify
    def total_pages(self):
        if self.hits > 0 < self._count:
            return int(math.ceil(float(self.hits) / float(self._count)) +
                       (len(self.uids_above) > 0))
        return 0

    @zeit.web.reify
    def pagination(self):
        if self.page > self.total_pages:
            raise pyramid.httpexceptions.HTTPNotFound()
        pagination = zeit.web.core.template.calculate_pagination(
            self.current_page, self.total_pages)
        return pagination if pagination is not None else []
