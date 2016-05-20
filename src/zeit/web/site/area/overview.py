# -*- coding: utf-8 -*-
import copy
import datetime
import dateutil
import logging
import zope.component

import zeit.solr.query

import zeit.web
import zeit.web.core.area.ranking


log = logging.getLogger(__name__)


SANITY_BOUND = 500


@zeit.web.register_area('overview')
class Overview(zeit.web.core.area.ranking.Ranking):

    count = SANITY_BOUND
    sort_order = 'publikation'

    @zeit.web.reify
    def start(self):
        return 0

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

    @zeit.web.reify
    def total_pages(self):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        total_pages = conf.get('total_news_pages', 30)

        if total_pages == 'all':
            return super(Overview, self).total_pages
        else:
            return int(conf.get('total_news_pages'))

    @zeit.web.reify
    def _today(self):
        return datetime.datetime.today().replace(
            hour=0, minute=0, second=0, microsecond=0)

    @zeit.web.reify
    def pagination_info(self):
        previous_day = (self._today+datetime.timedelta(
            days=self.current_page)).strftime("%Y-%m-%d")
        next_day = (self._today-datetime.timedelta(
            days=self.current_page)).strftime("%Y-%m-%d")
        return {
            'previous_label': u'Vorheriger Tag',
            'previous_param': dict(date=previous_day),
            'next_label': u'Nächster Tag',
            'next_param': dict(date=next_day)}

    def page_info(self, page_nr):
        if not page_nr:
            page_nr = 1
        date = self._today - datetime.timedelta(days=(page_nr-1))

        date_label = date.strftime("%d.%m")
        date_param = date.strftime("%Y-%m-%d")

        if page_nr == 1:
            date_label = date.strftime("%d.%m.%Y")

        return {
            'page_label': date_label,
            'remove_get_param': 'date',
            'append_get_param': dict(date=date_param)}

    def _page(self):
        return self.date_to_page(dateutil.parser.parse(
            self.request.GET['date']))

    def date_to_page(self, date):
        return (self._today-date).days + 1
