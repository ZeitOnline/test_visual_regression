# -*- coding: utf-8 -*-
import collections

import grokcore.component
import zope.component
import zope.schema

import zeit.cms.content.property
import zeit.content.cp.automatic
import zeit.content.cp.interfaces
import zeit.find.daterange
import zeit.find.search
import zeit.solr.interfaces

import zeit.web
import zeit.web.core.block


FIELDS = ' '.join([
    'date-last-published',
    'graphical-preview-url-large',
    'image-base-id',
    'image-expires',
    'image-type',
    'image-xml',
    'keyword',
    'last-semantic-change',
    'main_text',
    'ns-meta-type',
    'product_id',
    'ressort',
    'sub_ressort',
    'subtitle',
    'image',
    'supertitle',
    'teaser_text',
    'title',
    'type',
    'uniqueId',
    'uuid'
])


MODES = collections.OrderedDict([
    (None, (None, u'keine Einschränkung')),
    ('today', (zeit.find.daterange.today_range, u'Heute')),
    ('24h', (zeit.find.daterange.one_day_range, u'24 Stunden')),
    ('7d', (zeit.find.daterange.seven_day_range, u'7 Tage')),
    ('30d', (zeit.find.daterange.month_range, u'30 Tage')),
    ('1y', (zeit.find.daterange.year_range, u'1 Jahr'))
])


TYPES = collections.OrderedDict([
    ('article', u'Artikel'),
    # ('author', u'Autor'),
    # ('series', u'Serie'),
    # ('comment', u'Kommentar'),
    ('gallery', u'Fotostrecke'),
    ('video', u'Video'),
    # ('blog', u'Blogbeitrag')
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


BOOSTS = [
    '{!boost b=recip(ms(NOW,last-semantic-change),3.16e-11,1,1)}'
    '{!type=IntrafindQueryParser}'
]


ORDERS = collections.defaultdict(
    lambda: 'score desc',
    {'relevanz': 'score desc',
     'aktuell': 'last-semantic-change desc'}
)


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
        return list(these.intersection(TYPES.keys()))

    @property
    def type_choice(self):
        for key, label in TYPES.items():
            yield key, key in self.types, label

    @zeit.web.reify
    def mode(self):
        this = self['mode']
        return this in MODES and this or None

    @property
    def mode_choice(self):
        for key, (_, label) in MODES.items():
            yield key, key == self.mode, label

    @zeit.web.reify
    def sort_order(self):
        this = self['sort']
        return this in ORDERS and this or None

    @zeit.web.reify
    def raw_query(self):
        kw = {'published': 'true'}
        if self.query:
            kw['fulltext'] = self.query
        if self.mode:
            kw['from_'], kw['until'] = MODES[self.mode][0]()
        if self.types:
            kw['types'] = self.types
        query = zeit.find.search.query(**kw)
        return ''.join(BOOSTS + [query])


class IResultsArea(zeit.content.cp.interfaces.IAutomaticArea):

    sort_order = zope.schema.TextLine(default=u'score desc', required=False)


@grokcore.component.implementer(IResultsArea)
@grokcore.component.adapter(zeit.content.cp.interfaces.IArea)
class ResultsArea(zeit.content.cp.automatic.AutomaticArea):

    sort_order = zeit.cms.content.property.ObjectPathProperty(
        '.sort_order', IResultsArea['sort_order'])

    def values(self):
        result = []
        conn = zope.component.getUtility(zeit.solr.interfaces.ISolr)
        solr_result = list(conn.search(
            self.raw_query,
            # sort=self.sort_order,
            sort='score desc',
            rows=self.count,
            fl=FIELDS,
            **HIGHLIGHTING
        ))
        for block in self.context.values():
            if not zeit.content.cp.interfaces.IAutomaticTeaserBlock.providedBy(
                    block) or not len(solr_result):
                result.append(block)
                continue
            block.insert(0, zeit.cms.interfaces.ICMSContent(
                self._extract_newest(solr_result)))
            result.append(block)
        return result
