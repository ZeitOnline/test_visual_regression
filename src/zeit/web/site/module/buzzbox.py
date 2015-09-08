import logging

import zope.component

import zeit.content.cp.interfaces

import zeit.web
import zeit.web.site.module
import zeit.web.core.centerpage
import zeit.web.core.interfaces


log = logging.getLogger(__name__)


class Buzzbox(zeit.web.site.module.Module, list):

    header = None
    score_factor = 1

    @zeit.web.reify
    def reach(self):
        return zope.component.getUtility(zeit.web.core.interfaces.IReach)

    @zeit.web.reify
    def ressort(self):
        centerpage = zeit.content.cp.interfaces.ICenterPage(self.context)
        if not centerpage.ressort or centerpage.type == 'homepage':
            return
        return centerpage.ressort.lower()

    def __hash__(self):
        return hash((self.layout, self.ressort))


@zeit.web.register_module('mostread')
class MostreadBuzzbox(Buzzbox):

    header = 'Meistgelesene Artikel'
    label = 'Meist&shy;gelesen'

    def __init__(self, context):
        super(MostreadBuzzbox, self).__init__(context)
        self += self.reach.get_views(section=self.ressort)
        self.layout = 'buzz-mostread'
        self.icon = 'buzz-read'
        self.score_pattern = ['Keine Leser', '{} Leser']


@zeit.web.register_module('mostcommented')
class CommentsBuzzbox(Buzzbox):

    header = 'Meistkommentiert'
    label = 'Meist&shy;kommentiert'

    def __init__(self, context):
        super(CommentsBuzzbox, self).__init__(context)
        self += self.reach.get_comments(section=self.ressort)
        self.layout = 'buzz-comments'
        self.icon = 'buzz-comment'
        self.score_pattern = ['Keine Kommentare', '{} Kommentar', '{} Kommentare']


@zeit.web.register_module('mostshared')
class FacebookBuzzbox(Buzzbox):

    header = 'Meistgeteilt'
    label = 'Meist&shy;geteilt'

    def __init__(self, context):
        super(FacebookBuzzbox, self).__init__(context)
        self += self.reach.get_social(facet='facebook', section=self.ressort)
        self.layout = 'buzz-facebook'
        self.icon = 'buzz-shared'
        self.score_pattern = ['Nie geteilt', '{} mal geteilt']


@zeit.web.register_module('mosttrending')
class TrendingBuzzbox(Buzzbox):

    header = 'Aufsteigend'
    label = 'Aufsteigend'

    def __init__(self, context):
        super(TrendingBuzzbox, self).__init__(context)
        self += self.reach.get_trend(section=self.ressort)
        self.layout = 'buzz-trend'
        self.icon = 'buzz-trend'
        self.score_pattern = ['+ {0}']
        self.score_factor = 10000
