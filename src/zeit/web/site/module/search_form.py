import json
import collections
import logging

from zeit.solr import query as lq
import zeit.find.daterange

import zeit.web
import zeit.web.core.centerpage


log = logging.getLogger(__name__)


@zeit.web.register_module('search-form')
class Form(zeit.web.core.centerpage.Module):
    """Form module that renders as a searchbar with options.

    It validates user input taken from query parameters and constructs
    valid search queries and options.

    To display its results, the form needs a
    `zeit.web.core.area.ranking.Ranking` area on the same centerpage.
    The ranking area can have its `automatic_type` set to `search-query` or
    `elasticsearch-query`, to retrieve search results from a solr or
    elasticsearch server respectively.
    """

    ORDERS = [
        'aktuell',
        'relevanz',
        'publikation'
    ]
    MODES = collections.OrderedDict([
        ('today', 'Heute'),
        ('24h', '24 Stunden'),
        ('7d', '7 Tage'),
        ('30d', '30 Tage'),
        ('1y', '1 Jahr')
    ])
    TYPES = collections.OrderedDict([
        ('article', 'Artikel'),
        ('gallery', 'Fotostrecke'),
        ('video', 'Video')
    ])
    FIELDS = [
        'title',
        'teaser',
        'body',
        'payload.body.supertitle',
        'payload.body.subtitle',
        'payload.body.byline',
        'teaser_img_subline'
    ]

    @zeit.web.reify
    def search_term(self):
        """Search term as entered by the user.

        Defaults to None.
        """
        return u' '.join(self.request.GET.getall('q')) or None

    @zeit.web.reify
    def types(self):
        """A list of document types to narrow the search by.

        Is validated against allowed types and defaults to all of them.
        """
        in_types = set(t for t in self.request.GET.getall('type') if t)
        types = sorted(in_types.intersection(self.TYPES.keys()))
        return types or self.TYPES.keys()

    @property
    def type_choice(self):
        """Generates a list of available types for the template.

        Entries contain: document type, selection status, type label
        """
        for key, label in self.TYPES.items():
            yield key, key in self.types, label

    @zeit.web.reify
    def mode(self):
        """The URL-value of the selected time range.

        Named `mode` for historical reasons.
        Is validated against allowed modes and defaults to None.
        """
        mode = self.request.GET.get('mode')
        return mode in self.MODES and mode or None

    @zeit.web.reify
    def raw_mode(self):
        """Time range in solr query usable format"""
        return {
            'today': zeit.find.daterange.today_range(),
            '24h': zeit.find.daterange.one_day_range(),
            '7d': zeit.find.daterange.seven_day_range(),
            '30d': zeit.find.daterange.month_range(),
            '1y': zeit.find.daterange.year_range(),
        }.get(self.mode)

    @zeit.web.reify
    def elasticsearch_raw_mode(self):
        """Time range in elasticsearch query usable format"""
        if self.mode:
            return {
                'range': {
                    'payload.document.last-semantic-change': {
                        'gte': {
                            'today': 'now/d',
                            '24h': '24h',
                            '7d': '7d',
                            '30d': '30d',
                            '1y': '1y',
                        }.get(self.mode)
                    }
                }
            }

    @property
    def mode_choice(self):
        """Generates a list of available types for the template.

        Entries contain: mode key, selection status, mode label
        """
        for key, label in self.MODES.items():
            yield key, key == self.mode, label

    @zeit.web.reify
    def order(self):
        """The URL-value of the selected sort order.

        Defaults to 'aktuell'.
        """
        order = self.request.GET.get('sort')
        if self.search_term in (None, lq.any_value()) or (
                order not in self.ORDERS):
            return 'aktuell'
        return order

    @zeit.web.reify
    def raw_order(self):
        """Sort order in solr format"""
        return {
            'relevanz': 'score desc',
            'publikation': 'date_last_published asc'
        }.get(self.order, 'last-semantic-change desc')

    @zeit.web.reify
    def elasticsearch_raw_order(self):
        """Sort order in elasticsearch format"""
        return {
            'relevanz': '_score:desc',
            'publikation': 'payload.workflow.date_last_published_semantic:asc'
        }.get(self.order, 'payload.document.last-semantic-change:desc')

    @zeit.web.reify
    def raw_query(self):
        """Constructs a solr query with filters and restrictions"""
        tokens = collections.deque()
        if self.search_term:
            boost = (
                '{!boost b=recip(ms(NOW,last-semantic-change),3.16e-11,1,1)}'
                '{!type=IntrafindQueryParser}')
            tokens.append(boost + lq.quoted(self.search_term))

        if self.mode:
            tokens.append(lq.datetime_range(
                'last-semantic-change', *self.raw_mode))

        tokens.append(
            lq._field('type', lq.or_(*self.types)))

        restrictions = [lq.not_(lq._field(k, v)) for k, v in (
            ('product_id', lq.or_('News', 'afp', 'SID', 'ADV')),
            ('ressort', lq.or_('Administratives', 'News', 'Aktuelles')),
            ('expires', '[* TO NOW]')
        )]

        tokens.extend(restrictions)
        return ' '.join(tokens)

    @zeit.web.reify
    def elasticsearch_raw_query(self):
        """Constructs an elasticsearch query with filters and restrictions"""
        if self.search_term:
            query = {
                'simple_query_string': {
                    'query': self.search_term,
                    'fields': self.FIELDS
                }
            }
        else:
            query = {
                'match_all': {}
            }
        if self.order == 'relevanz':
            query = {
                'function_score': {
                    'query': query,
                    'linear': {
                        'payload.document.date-last-modified': {
                            'scale': '365d'
                        }
                    }
                }
            }
        must_not_clause = [
            {
                'terms': {'payload.workflow.product-id': [
                    'ADV', 'News', 'SID', 'afp']}
            }, {
                'terms': {'payload.document.ressort': [
                    'Administratives', 'Aktuelles', 'News']}
            }
        ]
        must_clause = [
            query,
            {
                'terms': {'payload.meta.type': self.types}
            }, {
                'term': {'payload.workflow.published': True}
            }
        ]
        if self.mode:
            must_clause.append(self.elasticsearch_raw_mode)

        query = {
            'bool': {
                'must_not': must_not_clause,
                'must': must_clause
            }
        }
        return json.dumps(query)
