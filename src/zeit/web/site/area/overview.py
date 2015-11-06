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


class Placeholder(object):

    def __init__(self, context):
        self.context = context

    def values(self):
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


@zeit.web.register_area('overview')
class Overview(zeit.web.site.area.ranking.Ranking):

    count = SANITY_BOUND
    sort_order = 'publikation'

    def values(self):
        self.context = Placeholder(self.context)  # Monkeypatch the context
        values = super(Overview, self).values()
        self.context = self.context.context
        return values

    def _query_solr(self, query, sort_order):
        query = self._build_query()
        return super(Overview, self)._query_solr(query, sort_order)

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
