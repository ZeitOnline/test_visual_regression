from pyramid.httpexceptions import HTTPMovedPermanently
from pyramid.view import view_config

import zeit.content.link.interfaces

import zeit.web.magazin.view


@view_config(context=zeit.content.link.interfaces.ILink,
             custom_predicates=(zeit.web.magazin.view.is_zmo_content,))
class Link(zeit.web.core.view.Content):

    def __call__(self):
        return HTTPMovedPermanently(location=self.context.url)
