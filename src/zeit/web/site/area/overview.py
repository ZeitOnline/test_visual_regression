# -*- coding: utf-8 -*-
import copy
import datetime
import logging

import dateutil
import grokcore.component
import zope.component

import zeit.solr.query

import zeit.web
import zeit.web.core.area.ranking


log = logging.getLogger(__name__)


SANITY_BOUND = 500


@zeit.web.register_area('overview')
class Overview(zeit.web.core.area.ranking.Ranking):
    """An automatic area that performs pagination for entire days, i.e.
    one day is one page.

    This means that the `count` of auto-teaser blocks is irrelevant here,
    in fact usually only one block is configured, and the area fills itself
    with as many blocks as there are results for that day.
    """

    count = SANITY_BOUND
    sort_order = 'publikation'

    @zeit.web.reify
    def start(self):
        return 0

    @zeit.web.reify
    def total_pages(self):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        total_pages = conf.get('total_news_pages', '30')

        if total_pages == 'all':
            return super(Overview, self).total_pages
        else:
            return int(total_pages)

    @zeit.web.reify
    def today(self):
        return datetime.datetime.today().replace(
            hour=0, minute=0, second=0, microsecond=0)

    @zeit.web.reify
    def pagination_info(self):
        previous_day = (self.today + datetime.timedelta(
            days=self.current_page)).strftime("%Y-%m-%d")
        next_day = (self.today - datetime.timedelta(
            days=self.current_page)).strftime("%Y-%m-%d")
        return {
            'previous_label': u'Nächster Tag',
            'previous_param': dict(date=previous_day),
            'next_label': u'Vorheriger Tag',
            'next_param': dict(date=next_day)}

    def page_info(self, page_nr):
        if not page_nr:
            page_nr = 1
        date = self.today - datetime.timedelta(days=(page_nr - 1))

        date_label = date.strftime("%d.%m")
        date_param = date.strftime("%Y-%m-%d")

        if (page_nr == self.total_pages or
            page_nr == self.current_page or
                date_label == "31.12"):
                    date_label = date.strftime("%d.%m.%Y")

        return {
            'page_label': date_label,
            'remove_get_param': 'date',
            'append_get_param': dict(date=date_param)}

    def _page(self):
        return self.date_to_page(dateutil.parser.parse(
            self.request.GET['date']))

    @zeit.web.reify
    def _pagination(self):
        return zeit.web.core.template.calculate_pagination(
            self.current_page, self.total_pages, slots=6)

    def date_to_page(self, date):
        return (self.today - date).days + 1


class DateContentQuery(zeit.web.core.area.ranking.SolrContentQuery):

    grokcore.component.context(Overview)

    def __init__(self, context):
        super(DateContentQuery, self).__init__(context)
        self.query_string = zeit.solr.query.and_(
            self.query_string, self._range_query())

    def __call__(self):
        result = super(DateContentQuery, self).__call__()
        self._fill_up_blocks_to_match_total_hits()
        return result

    def _fill_up_blocks_to_match_total_hits(self):
        # XXX This actually rather is the responsibility of the Area, but we
        # cannot do it there at the proper time (when total_hits is available,
        # but before auto blocks are filled with the query content).
        area = self.context.context
        values = area.values()
        length = len(values)
        if length and self.total_hits > length:
            overhang = min(self.total_hits, SANITY_BOUND) - length
            for clone in self.clone_factory(values[-1], overhang):
                area.add(clone)

    @staticmethod
    def clone_factory(jango, count):
        for _ in range(count):
            xml = copy.copy(jango.xml)
            xml.attrib.pop('{http://namespaces.zeit.de/CMS/cp}__name__', None)
            clone = type(jango)(jango.__parent__, xml)
            yield clone

    def _range_query(self):
        offset = datetime.timedelta(days=self.context.current_page - 1)
        today = self.context.today - offset
        tomorrow = today + datetime.timedelta(days=1)
        range_ = zeit.solr.query.datetime_range(
            'date_first_released',
            datetime.datetime.combine(today, datetime.time()),
            datetime.datetime.combine(tomorrow, datetime.time()))
        return range_
