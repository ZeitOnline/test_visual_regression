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

    @zeit.web.reify
    def reach(self):
        return zope.component.getUtility(zeit.web.core.interfaces.IReach)

    @zeit.web.reify
    def ressort(self):
        centerpage = zeit.content.cp.interfaces.ICenterPage(self.context)
        if not centerpage.ressort or centerpage.type == 'homepage':
            return
        return centerpage.ressort.lower()


@zeit.web.register_module('mostread')
class MostreadBuzzbox(Buzzbox):

    header = 'Meistgelesene Artikel'

    def __init__(self, context):
        super(MostreadBuzzbox, self).__init__(context)
        self += self.reach.get_views(section=self.ressort)
        self.layout = 'buzz-mostread'


@zeit.web.register_module('mostcommented')
class CommentsBuzzbox(Buzzbox):

    header = 'Meistkommentiert'

    def __init__(self, context):
        super(CommentsBuzzbox, self).__init__(context)
        self += self.reach.get_comments(section=self.ressort)
        self.layout = 'buzz-comments'


@zeit.web.register_module('mostshared')
class FacebookBuzzbox(Buzzbox):

    header = 'Meistgeteilt'

    def __init__(self, context):
        super(FacebookBuzzbox, self).__init__(context)
        self += self.reach.get_social(facet='facebook', section=self.ressort)
        self.layout = 'buzz-facebook'
