import logging

import zope.component

import zeit.content.cp.interfaces

import zeit.web
import zeit.web.core.centerpage
import zeit.web.core.interfaces


log = logging.getLogger(__name__)


class Buzzbox(zeit.web.core.centerpage.Module, list):

    header = None
    score_factor = 1

    def __init__(self, context):
        super(Buzzbox, self).__init__(context)
        self.layout = 'buzzbox'

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
        return hash((self.identification, self.ressort))


@zeit.web.register_module('zmo-mostread')
class MostreadBuzzbox(Buzzbox):

    label = 'Meistgelesen'

    def __init__(self, context):
        super(MostreadBuzzbox, self).__init__(context)
        self += self.reach.get_views(section='zeit-magazin')
        self.identification = 'zmo-mostread'
        self.score_pattern = ['Keine Leser', '{} Leser', '{} Leser']
        self.icon = 'buzz-read'


@zeit.web.register_module('zmo-mostcommented')
class CommentsBuzzbox(Buzzbox):

    label = 'Kommentiert'

    def __init__(self, context):
        super(CommentsBuzzbox, self).__init__(context)
        self += self.reach.get_comments(section='zeit-magazin')
        self.identification = 'zmo-mostcommented'
        self.score_pattern = [
            'Keine Kommentare', '{} Kommentar', '{} Kommentare']
        self.icon = 'buzz-comment'


@zeit.web.register_module('zmo-mostliked')
class FacebookBuzzbox(Buzzbox):

    label = 'Auf Facebook'

    def __init__(self, context):
        super(FacebookBuzzbox, self).__init__(context)
        self += self.reach.get_social(facet='facebook', section='zeit-magazin')
        self.identification = 'zmo-mostliked'
        self.score_pattern = [
            'Keine Empfehlungen', '{} Empfehlung', '{} Empfehlungen']
        self.icon = 'buzz-shared'
