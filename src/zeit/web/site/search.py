import datetime

import zeit.web
import zeit.web.core.block


@zeit.web.register_module('search-form')
class Search(zeit.web.core.block.Module):

    @zeit.web.reify
    def query(self):
        return 'Kartoffelsalat AND Mayonnaise'

    @zeit.web.reify
    def title(self):
        return 'Suchformular'

    @zeit.web.reify
    def ranges(self):
        today = datetime.date.today()
        return [
            ('today', today.strftime('%Y-%m-%d'), 'Heute'),
            ('one-day', 'NOW-1DAY', '24 Stunden'),
            ('seven-days', 'NOW-7DAY', '7 Tage'),
            ('thirty-days', 'NOW-30DAY', '30 Tage'),
            ('this-year', today.strftime('%Y-01-01'), 'Dieses Jahr')
        ]

    @zeit.web.reify
    def types(self):
        return [
            ('article', 'Artikel'),
            ('author', 'Autor'),
            ('series', 'Serie'),
            # ('comment', 'Kommentar'),
            ('gallery', 'Fotostrecke'),
            ('video', 'Video')
            # ('blog', 'Blogbeitrag')
        ]
