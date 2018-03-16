# -*- coding: utf-8 -*-
import math

import pyramid.httpexceptions
import pyramid.threadlocal
import zope.interface

import zeit.content.cp.automatic
import zeit.content.cp.interfaces

import zeit.web
import zeit.web.core.centerpage
import zeit.web.core.interfaces
import zeit.web.core.template
import zeit.web.core.utils


@zeit.web.register_area('ranking')
class Ranking(zeit.content.cp.automatic.AutomaticArea):
    """An automatic area that provides solr-based pagination of results.

    Optionally supports a `search-form` cpextra so the query can be entered
    by the user instead of reading it from the area.

    Supports manual content on the first page, and then automatic content on
    the following pages: On the first page, if there are manual teasers,
    Ranking claims to have count=0 (so it is effectively hidden), and on the
    following pages, zeit.web.core.view_centerpage.CenterpagePage hides most
    other areas/modules except for the Ranking area.
    """

    zope.interface.implements(
        zeit.content.cp.interfaces.IArea,
        zeit.web.core.interfaces.IPagination
    )

    def __init__(self, context):
        super(Ranking, self).__init__(context)
        self.request = pyramid.threadlocal.get_current_request()

    @zeit.web.reify
    def search_form(self):
        centerpage = zeit.content.cp.interfaces.ICenterPage(self.context)
        module = zeit.web.core.utils.find_block(
            centerpage, module='search-form')
        return zeit.web.core.centerpage.get_module(module)

    def values(self):
        return self._values

    @zeit.web.reify
    def _values(self):
        return super(Ranking, self).values()

    @property
    def query_string(self):
        return self.search_form.search_term

    @property
    def raw_query(self):
        if self.search_form:
            return self.search_form.raw_query
        return super(Ranking, self).raw_query

    @property
    def elasticsearch_raw_query(self):
        if self.search_form:
            return self.search_form.elasticsearch_raw_query
        return super(Ranking, self).elasticsearch_raw_query

    @property
    def raw_order(self):
        if self.search_form:
            return self.search_form.raw_order
        return super(Ranking, self).raw_order

    @property
    def elasticsearch_raw_order(self):
        if self.search_form:
            return self.search_form.elasticsearch_raw_order
        return super(Ranking, self).elasticsearch_raw_order

    @property
    def sort_order(self):
        if self.search_form:
            return self.search_form.order

    @zeit.web.reify
    def surrounding_teasers(self):
        if self.hide_dupes:
            return len(self._content_query.existing_teasers)
        else:
            return 0

    @zeit.web.reify
    def query(self):
        param = u' '.join(self.request.GET.getall('q'))
        if param and self.search_form:
            return param

    @zeit.web.reify
    def hits(self):
        self.values()
        try:
            return int(self._content_query.total_hits)
        except TypeError:
            return 0

    @zeit.web.reify
    def start(self):
        return self.count * max(
            self.page - 1 - int(self.surrounding_teasers > 0), 0)

    @zeit.web.reify
    def count(self):
        if self.page == 1 and self.surrounding_teasers > 0:
            return 0
        return self.context._count

    def _page(self):
        # We might calculate the page from a different
        # GET param, e.g. date in zeit.web.site.area.overwiew
        return int(self.request.GET['p'])

    @zeit.web.reify
    def pagination_info(self):
        return {
            'previous_label': u'Vorherige Seite',
            'next_label': u'Nächste Seite'}

    def page_info(self, page_nr):
        url = zeit.web.core.utils.remove_get_params(self.request.url, 'p')
        if page_nr > 1:
            url = zeit.web.core.utils.add_get_params(url, **dict(p=page_nr))

        return {
            'label': page_nr,
            'url': url
        }

    @zeit.web.reify
    def page(self):
        try:
            page = self._page()
            assert page > 0
            if page == 1 and not self.is_sitemap:
                raise pyramid.httpexceptions.HTTPMovedPermanently(
                    zeit.web.core.template.remove_get_params(
                        self.request.url, 'p'))
            return page
        except (AssertionError, ValueError):
            raise pyramid.httpexceptions.HTTPNotFound()
        except KeyError:
            return 1

    @zeit.web.reify
    def current_page(self):
        return self.page  # Compat to article pagination

    @zeit.web.reify
    def total_pages(self):
        count = self.context._count
        if self.hits > 0 < count:
            return int(math.ceil(float(self.hits) / float(count)) +
                       int(self.surrounding_teasers > 0))
        return 0

    @zeit.web.reify
    def _pagination(self):
        return zeit.web.core.template.calculate_pagination(
            self.current_page, self.total_pages)

    @zeit.web.reify
    def pagination(self):
        if self.page > self.total_pages:
            return []
        pagination = self._pagination
        return pagination if pagination is not None else []

    @property
    def is_sitemap(self):
        return zeit.content.cp.interfaces.ISitemap.providedBy(
            zeit.content.cp.interfaces.ICenterPage(self))
