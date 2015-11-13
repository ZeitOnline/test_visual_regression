import copy
import datetime
import logging

import zeit.solr.query

import zeit.web
import zeit.web.core.date
import zeit.web.site.area.ranking


log = logging.getLogger(__name__)


SANITY_BOUND = 500


@zeit.web.register_area('overview')
class Overview(zeit.web.site.area.ranking.Ranking):

    count = SANITY_BOUND
    sort_order = 'publikation'

    @staticmethod
    def clone_factory(jango, count):
        for _ in range(count):
            xml = copy.copy(jango.xml)
            xml.attrib.pop('{http://namespaces.zeit.de/CMS/cp}__name__', None)
            clone = type(jango)(jango.__parent__, xml)
            yield clone

    def _query_solr(self, query, sort_order):
        query = self._build_query()
        result = super(Overview, self)._query_solr(query, sort_order)
        values = self.context.values()
        length = len(values)
        if length and self.hits > length:
            overhang = min(self.hits, SANITY_BOUND) - length
            for clone in self.clone_factory(values[-1], overhang):
                self.context.add(clone)
        return result

    def _build_query(self):
        offset = datetime.timedelta(days=self.current_page - 1)
        today = datetime.date.today() + offset
        tomorrow = today + datetime.timedelta(days=1)
        range_ = zeit.solr.query.datetime_range(
            'date_first_released',
            datetime.datetime.combine(today, datetime.time()),
            datetime.datetime.combine(tomorrow, datetime.time()))
        query = zeit.find.search.query(filter_terms=[
            zeit.solr.query.field_raw('published', 'published*')])
        return zeit.solr.query.and_(query, range_)
