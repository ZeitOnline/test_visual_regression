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
        IRanking,
        zeit.web.core.interfaces.IPagination
    )

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

    @zeit.web.reify
    def query_string(self):
        param = u' '.join(self.request.GET.getall('q'))
        if param and self.raw_query:
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


class Converter(object):

    def _convert(self, doc):
        doc = self._convert_names(doc)
        doc = self._convert_dates(doc)
        doc = self._set_defaults(doc)
        return doc

    FIELD_MAP = NotImplemented

    def _convert_names(self, doc):
        for source, target in self.FIELD_MAP.items():
            try:
                doc[target] = doc[source]
            except KeyError:
                continue
        return doc

    DATE_FIELDS = [
        'date_last_modified',
        'date_first_released',
        'last_semantic_change',
        'date_last_published',
        'date_last_published_semantic',
    ]

    def _convert_dates(self, doc):
        for key in self.DATE_FIELDS:
            try:
                doc[key] = zc.iso8601.parse.datetimetz(str(doc[key]))
            except (KeyError, UnicodeEncodeError, ValueError):
                continue
        return doc

    def _set_defaults(self, doc):
        # XXX These asset badges and classification flags are not indexed
        #     in Solr, so we lie about them.
        for name in ['gallery', 'genre', 'template', 'video', 'video_2']:
            doc.setdefault(name, None)
        doc.setdefault('lead_candidate', False)
        doc.setdefault('commentSectionEnable', True)
        return doc


class SolrContentQuery(zeit.content.cp.automatic.SolrContentQuery,
                       Converter):

    grokcore.component.context(Ranking)

    FIELD_MAP = {
        'authors': 'authorships',
        'date-last-modified': 'date_last_modified',
        'date_first_released': '',
        'date_last_published': '',
        'date_last_published_semantic': 'date_last_published_semantic',
        'image-base-id': 'teaser_image',
        'image-fill-color': 'teaser_image_fill_color',
        'last-semantic-change': 'last_semantic_change',
        'lead_candidate': '',
        'product_id': '',
        'serie': '',
        'show_commentthread': 'commentSectionEnable',
        'supertitle': 'teaserSupertitle',
        'teaser_text': 'teaserText',
        'title': 'teaserTitle',
        'type': 'doc_type',
        'uniqueId': '',
    }

    @zeit.web.reify
    def FIELDS(self):
        return ' '.join(self.FIELD_MAP.keys())

    def _convert(self, doc):
        doc = super(SolrContentQuery, self)._convert(doc)
        for key in ['teaser_image', 'teaser_image_fill_color']:
            if doc.get(key):
                doc[key] = doc[key][0]
        return doc

    def _resolve(self, doc):
        return zeit.cms.interfaces.ICMSContent(self._convert(doc), None)


class TMSContentQuery(zeit.content.cp.automatic.TMSContentQuery,
                      Converter):

    grokcore.component.context(Ranking)

    # XXX Can we generate this from zeit.retresco.convert somehow?
    FIELD_MAP = {
        'authors': 'authorships',
        'date_last_semantic_change': 'last_semantic_change',
        'allow_comments': 'commentsAllowed',
        'show_comments': 'commentSectionEnable',
        'print_ressort': 'printRessort',
        'teaser_text': 'teaserText',
        'teaser_title': 'teaserTitle',
        'teaser_supertitle': 'teaserSupertitle',
        'article_genre': 'genre',
        'article_template': 'template',
    }

    def _resolve(self, doc):
        return zeit.cms.interfaces.ICMSContent(self._convert(doc), None)
