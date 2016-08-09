# -*- coding: utf-8 -*-
import logging
import math

import grokcore.component
import pyramid
import zc.iso8601.parse
import zope.schema

import zeit.content.cp.automatic
import zeit.content.cp.interfaces

import zeit.web
import zeit.web.core.centerpage
import zeit.web.core.interfaces
import zeit.web.core.template


log = logging.getLogger(__name__)


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
        IRanking,
        zeit.web.core.interfaces.IPagination
    )

    FIELDS = ' '.join([
        'authors',
        'date-last-modified',
        'date_first_released',
        'date_last_published',
        'image-base-id',
        'image-fill-color',
        'last-semantic-change',
        'lead_candidate',
        'product_id',
        'show_commentthread',
        'serie',
        'supertitle',
        'teaser_text',
        'title',
        'type',
        'uniqueId',
    ])

    FIELD_MAP = [
        (u'authors', u'authorships'),
        (u'show_commentthread', u'commentSectionEnable'),
        (u'supertitle', u'teaserSupertitle'),
        (u'teaser_text', u'teaserText'),
        (u'title', u'teaserTitle'),
    ]

    DATE_MAP = [
        (u'date-last-modified', u'date_last_modified'),
        (u'date_first_released', u'date_first_released'),
        (u'last-semantic-change', u'last_semantic_change'),
        (u'date_last_published', u'date_last_published'),
        (u'date_last_published', u'date_last_published_semantic'),
    ]

    def __init__(self, context):
        super(Ranking, self).__init__(context)
        self.request = pyramid.threadlocal.get_current_request()
        centerpage = zeit.content.cp.interfaces.ICenterPage(context)
        module = zeit.web.core.utils.find_block(
            centerpage, module='search-form')
        self.search_form = zeit.web.core.centerpage.get_module(module)

    def values(self):
        return self._values

    @zeit.web.reify
    def _values(self):
        return super(Ranking, self).values()

    @property
    def raw_query(self):
        if self.search_form:
            return self.search_form.raw_query
        else:
            return super(Ranking, self).raw_query

    @property
    def raw_order(self):
        if self.search_form:
            return self.search_form.raw_order
        else:
            return super(Ranking, self).raw_order

    @property
    def sort_order(self):
        if self.search_form:
            return self.search_form.sort_order

    @zeit.web.reify('default_term')
    def existing_uids(self):
        if not self.hide_dupes:
            return zeit.web.dont_cache([])
        return [x.uniqueId for x in self._content_query.existing_teasers
                if hasattr(x, 'uniqueId')]

    def document_hook(self, doc):
        for source, target in self.FIELD_MAP:
            try:
                doc[target] = doc[source]
            except KeyError:
                continue

        for source, target in self.DATE_MAP:
            try:
                doc[target] = zc.iso8601.parse.datetimetz(str(doc[source]))
            except (KeyError, UnicodeEncodeError, ValueError):
                continue

        serie = doc.get('serie', None)
        source = zeit.cms.content.interfaces.ICommonMetadata['serie'].source
        doc['serie'] = source.factory.values.get(serie, None)

        # XXX These asset badges and classification flags are not indexed
        #     in Solr, so we lie about them.
        doc.update({'gallery': None,
                    'genre': None,
                    'template': None,
                    'video': None,
                    'video_2': None})

        doc.setdefault('lead_candidate', False)
        doc.setdefault('commentSectionEnable', True)

        return doc

    @zeit.web.reify
    def query_string(self):
        param = u' '.join(self.request.GET.getall('q'))
        if param and self.raw_query:
            return param

    @zeit.web.reify
    def hits(self):
        self.values()
        return self._content_query.total_hits

    @zeit.web.reify
    def start(self):
        return self.count * max(
            self.page - 1 - (len(self.existing_uids) > 0), 0)

    @zeit.web.reify
    def count(self):
        if self.page == 1 and len(self.existing_uids) > 0:
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
            'previous_param': dict(p=self.current_page - 1),
            'next_label': u'Nächste Seite',
            'next_param': dict(p=self.current_page + 1)}

    def page_info(self, page_nr):
        return {
            'page_label': page_nr,
            'remove_get_param': 'p',
            'append_get_param': dict(p=page_nr)}

    @zeit.web.reify
    def page(self):
        try:
            page = self._page()
            assert page > 0
            if page == 1:
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
                       (len(self.existing_uids) > 0))
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


class SolrContentQuery(zeit.content.cp.automatic.SolrContentQuery):

    grokcore.component.context(Ranking)

    @property
    def FIELDS(self):
        return self.context.FIELDS

    def _resolve(self, solr_result):
        doc = self.context.document_hook(solr_result)
        return zeit.cms.interfaces.ICMSContent(doc, None)
