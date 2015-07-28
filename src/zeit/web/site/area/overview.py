import datetime
import itertools
import logging
import uuid

import zeit.solr.query

import zeit.web
import zeit.web.core.date
import zeit.web.site.area.ranking


log = logging.getLogger(__name__)


SANITY_BOUND = 500

DATE_MAP = [
    (u'date-last-modified', u'date_last_modified'),
    (u'date_first_released', u'date_first_released'),
    (u'last-semantic-change', u'last_semantic_change'),
    (u'date_last_published', u'date_last_published'),
    (u'date_last_published', u'date_last_published_semantic')
]


@zeit.web.register_area('overview')
class Overview(zeit.web.site.area.ranking.Ranking):

    count = SANITY_BOUND
    sort_order = 'publikation'

    @property
    def placeholder(self):
        values = self.context.values()
        length = len(values)
        if not length or self.hits <= length:
            return iter(values)
        overhang = min(self.hits, SANITY_BOUND) - length
        clones = self.clone_factory(values[-1], overhang)
        return itertools.chain(values, clones)

    @staticmethod
    def clone_factory(jango, count):
        for _ in range(count):
            clone = type(jango)(jango.__parent__, jango.xml)
            clone.__name__ = str(uuid.uuid4())
            yield clone

    def document_hook(self, doc):
        doc = super(Overview, self).document_hook(doc)
        for source, target in DATE_MAP:
            try:
                doc[target] = isinstance(doc[source], unicode) and (
                    zeit.web.core.date.parse_date(
                        doc[source], '%Y-%m-%dT%H:%M:%SZ')) or doc[source]
            except KeyError:
                continue
        return doc

    def _build_query(self):
        offset = datetime.timedelta(days=self.current_page - 1)
        today = datetime.date.today() + offset
        tomorrow = today + datetime.timedelta(days=1)
        range_ = zeit.solr.query.datetime_range(
            'date_first_released',
            datetime.datetime.combine(today, datetime.time()),
            datetime.datetime.combine(tomorrow, datetime.time()))
        query = super(Overview, self)._build_query()
        return zeit.solr.query.and_(query, range_)
