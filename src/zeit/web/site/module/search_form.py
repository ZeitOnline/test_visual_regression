import collections
import logging

from zeit.solr import query as lq
import zeit.cms.content.property
import zeit.content.cp.automatic
import zeit.content.cp.interfaces
import zeit.find.daterange
import zeit.find.search
import zeit.solr.interfaces

import zeit.web
import zeit.web.core.centerpage
import zeit.web.core.template
import zeit.web.site.area.ranking


log = logging.getLogger(__name__)


BOOSTS = ''.join([
    '{!boost b=recip(ms(NOW,last-semantic-change),3.16e-11,1,1)}',
    '{!type=IntrafindQueryParser}'
])


MODES = collections.OrderedDict([
    ('today', (zeit.find.daterange.today_range, 'Heute')),
    ('24h', (zeit.find.daterange.one_day_range, '24 Stunden')),
    ('7d', (zeit.find.daterange.seven_day_range, '7 Tage')),
    ('30d', (zeit.find.daterange.month_range, '30 Tage')),
    ('1y', (zeit.find.daterange.year_range, '1 Jahr'))
])


ORDERS = collections.defaultdict(
    lambda: 'last-semantic-change desc', {
        'relevanz': 'score desc',
        'aktuell': 'last-semantic-change desc',
        'publikation': 'date_last_published asc'}
)


RESTRICTIONS = [lq.not_(lq._field(k, v)) for k, v in (
    ('product_id', lq.or_('News', 'afp', 'SID', 'ADV')),
    ('ressort', lq.or_('Administratives', 'News', 'Aktuelles')),
    ('expires', '[* TO NOW]')
)]


TYPES = collections.OrderedDict([
    ('article', 'Artikel'),
    ('gallery', 'Fotostrecke'),
    ('video', 'Video')
])


@zeit.web.register_module('search-form')
class Form(zeit.web.core.centerpage.Module):

    @zeit.web.reify
    def query(self):
        return u' '.join(self.request.GET.getall('q')) or None

    @zeit.web.reify
    def types(self):
        types = set(t for t in self.request.GET.getall('type') if t)
        if len(types):
            return list(types.intersection(TYPES.keys()))
        else:
            return TYPES.keys()

    @property
    def type_choice(self):
        for key, label in TYPES.items():
            yield key, key in self.types, label

    @zeit.web.reify
    def mode(self):
        mode = self.request.GET.get('mode')
        return mode in MODES and mode or None

    @property
    def mode_choice(self):
        for key, (_, label) in MODES.items():
            yield key, key == self.mode, label

    @zeit.web.reify
    def sort_order(self):
        if self.query in (None, lq.any_value()):
            return 'aktuell'
        order = self.request.GET.get('sort')
        return order if order in ORDERS else 'aktuell'

    @zeit.web.reify
    def raw_order(self):
        return ORDERS[self.sort_order]

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
