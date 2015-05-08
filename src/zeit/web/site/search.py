import collections
import logging

import grokcore.component
import zope.component
import zope.schema

import zeit.cms.content.property
import zeit.content.cp.automatic
import zeit.content.cp.interfaces
import zeit.find.daterange
import zeit.find.search
import zeit.solr.interfaces
from zeit.solr import query as lq

import zeit.web
import zeit.web.core.block


log = logging.getLogger(__name__)


FIELDS = ' '.join([
    # 'date-last-published',
    # 'graphical-preview-url-large',
    # 'image-base-id',
    # 'image-expires',
    # 'image-type',
    # 'image-xml',
    # 'keyword',
    # 'last-semantic-change',
    # 'main_text',
    # 'ns-meta-type',
    # 'product_id',
    # 'ressort',
    # 'sub_ressort',
    # 'subtitle',
    # 'image',
    # 'supertitle',
    # 'teaser_text',
    # 'title',
    # 'type',
    'uniqueId',
    # 'uuid'
])


MODES = collections.OrderedDict([
    ('today', (zeit.find.daterange.today_range, 'Heute')),
    ('24h', (zeit.find.daterange.one_day_range, '24 Stunden')),
    ('7d', (zeit.find.daterange.seven_day_range, '7 Tage')),
    ('30d', (zeit.find.daterange.month_range, '30 Tage')),
    ('1y', (zeit.find.daterange.year_range, '1 Jahr'))
])


TYPES = collections.OrderedDict([
    ('article', 'Artikel'),
    # ('author', 'Autor'),
    # ('series', 'Serie'),
    # ('comment', 'Kommentar'),
    ('gallery', 'Fotostrecke'),
    ('video', 'Video'),
    # ('blog', 'Blogbeitrag')
])


HIGHLIGHTING = {
    'hl': 'true',
    'hl.fl': 'main_text,teaser_text',
    'hl.highlightMultiTerm': 'true',
    'hl.fragsize': '250',
    'hl.alternateField': 'teaser_text',
    'hl.snippets': '1',
    'hl.mergeContiguous': 'true',
    'hl.usePhraseHighlighter': 'true',
    'hl.simple.pre': '%3Cb%3E',
    'hl.simple.post': '%3C/b%3E'
}


BOOSTS = ''.join([
    '{!boost b=recip(ms(NOW,last-semantic-change),3.16e-11,1,1)}',
    '{!type=IntrafindQueryParser}'
])


ORDERS = collections.defaultdict(
    lambda: 'score desc', {
        'aktuell': 'last-semantic-change desc'}
)


RESTRICTIONS = [lq.not_(lq._field(k, v)) for k, v in {
    'product_id': lq.or_('News', 'afp', 'SID', 'ADV'),
    'ressort': lq.or_('Administratives', 'News', 'Aktuelles'),
    'expires': '[* TO NOW]'
}.items()]


@zeit.web.register_module('search-form')
class Form(zeit.web.core.block.Module):

    def __setitem__(self, key, value):
        self.context.xml.set(key, value or '')

    def __getitem__(self, key):
        return self.context.xml.get(key, '') or None

    @zeit.web.reify
    def query(self):
        return self['q']

    @zeit.web.reify
    def types(self):
        these = set((self['type'] or '').split())
        if len(these):
            return list(these.intersection(TYPES.keys()))
        else:
            return TYPES.keys()

    @property
    def type_choice(self):
        for key, label in TYPES.items():
            yield key, key in self.types, label

    @zeit.web.reify
    def mode(self):
        this = self['mode']
        return this in MODES and this or None

    @zeit.web.reify
    def page(self):
        try:
            return abs(int(self['page']))
        except (TypeError, ValueError):
            return 1

    @property
    def mode_choice(self):
        for key, (_, label) in MODES.items():
            yield key, key == self.mode, label

    @zeit.web.reify
    def sort_order(self):
        if self.query in (None, lq.any_value()):
            return 'aktuell'
        this = self['sort']
        return this in ORDERS and this or 'relevanz'

    @zeit.web.reify
    def raw_query(self):
        tokens = collections.deque()
        if self.query:
            tokens.append(BOOSTS + lq.quoted(self.query))
        if self.mode:
            tokens.append(lq.datetime_range(
                'last-semantic-change', *MODES[self.mode][0]()))
        tokens.append(
            lq._field('type', lq.or_(*(self.types or TYPES.keys()))))
        tokens.extend(RESTRICTIONS)
        return ' '.join(tokens)


class IResultsArea(zeit.content.cp.interfaces.IArea):

    sort_order = zope.schema.TextLine(
        title=u'Search result order', default=u'relevanz', required=False)

    hits = zope.schema.Int(
        title=u'Search result count', default=None, required=False)

    page = zope.schema.Int(
        title=u'Search result page', default=None, required=False)


@grokcore.component.implementer(IResultsArea)
@grokcore.component.adapter(zeit.content.cp.interfaces.IArea)
class ResultsArea(zeit.content.cp.automatic.AutomaticArea):

    sort_order = zeit.cms.content.property.ObjectPathProperty(
        '.sort_order', IResultsArea['sort_order'])

    query = zeit.cms.content.property.ObjectPathProperty(
        '.query', IResultsArea['query'])

    page = zeit.cms.content.property.ObjectPathProperty(
        '.page', IResultsArea['page'])

    _hits = zeit.cms.content.property.ObjectPathProperty(
        '.hits', IResultsArea['hits'])

    def values(self):
        return self._values

    @zeit.web.reify
    def _values(self):
        result = []
        conn = zope.component.getUtility(zeit.solr.interfaces.ISolr)
        solr_result = conn.search(
            self.raw_query, sort=ORDERS[self.sort_order], rows=self.count,
            fl=FIELDS, start=self.page, **HIGHLIGHTING)
        docs = collections.deque(solr_result)
        self.hits = solr_result.hits
        for block in self.context.values():
            if not zeit.content.cp.interfaces.IAutomaticTeaserBlock.providedBy(
                    block) or not len(docs):
                result.append(block)
                continue
            unique_id = docs.popleft().get('uniqueId')
            try:
                block.insert(0, zeit.cms.interfaces.ICMSContent(unique_id))
            except TypeError, err:
                log.debug('Corrupted search result', unique_id, err)
                continue
            result.append(block)
        return result

    @property
    def hits(self):
        if self._hits is None:
            return len(self.values()) and self._hits
        else:
            return 0

    @hits.setter
    def hits(self, value):
        if self._hits is None:
            self._hits = value

    @zeit.web.reify
    def total_pages(self):
        return 0

    @zeit.web.reify
    def current_page(self):
        return 0

    @zeit.web.reify
    def next_page(self):
        return 0

    @zeit.web.reify
    def pagination(self):
        return []
