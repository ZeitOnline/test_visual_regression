# -*- coding: utf-8 -*-
import datetime
import logging

import zeit.web
import zeit.web.core.area.automatic
import zeit.web.core.area.ranking


log = logging.getLogger(__name__)


FIRST_YEAR = 1946


@zeit.web.register_area('volume-year-pager')
class VolumeYearPager(zeit.web.core.area.ranking.Ranking):
    """An automatic area that performs pagination over years, i.e.
    one year is one page.

    This means that the `count` of auto-teaser blocks is irrelevant here,
    in fact usually only one block is configured, and the area fills itself
    with as many blocks as there are results for that year.
    """

    @zeit.web.reify
    def meta_robots(self):
        return 'index'

    @zeit.web.reify
    def total_pages(self):
        return self.__current_year() - FIRST_YEAR + 1

    @zeit.web.reify
    def current_page(self):
        return self.__year_to_page(self.__current_page_year())

    @zeit.web.reify
    def pagination_info(self):
        return {
            'previous_label': u'Nächstes Jahr',
            'previous_url': self.__url_for_year(
                self.__current_page_year() + 1),
            'next_label': u'Vorheriges Jahr',
            'next_url': self.__url_for_year(self.__current_page_year() - 1)}

    def page_info(self, page_nr):
        if not page_nr:
            page_nr = 1
        page_year = self.__page_to_year(page_nr)
        return {
            'page_label': page_year,
            'url': self.__url_for_year(page_year)}

    @zeit.web.reify
    def _pagination(self):
        return zeit.web.core.template.calculate_pagination(
            self.current_page, self.total_pages, slots=6)

    """ The real current year (anno domini) """
    def __current_year(self):
        return datetime.datetime.today().year

    """ The year which the user is viewing (chosen via URL) """
    def __current_page_year(self):
        # XXX: looks fragile. Can we read this from page XML data?
        return int(self.request.path.lstrip('/').split('/')[0])

    def __year_to_page(self, year):
        return (self.__current_year() - year) + 1

    def __page_to_year(self, page):
        return self.__current_year() - page + 1

    def __url_for_year(self, year):
        # XXX: do we have a scheme+host variable available for areas?
        return '{}://{}/{}/index'.format(
            self.request.scheme, self.request.host, year)
