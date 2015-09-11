from pyramid.httpexceptions import HTTPMovedPermanently
from pyramid.view import view_config

import zeit.content.link.interfaces


@view_config(context=zeit.content.link.interfaces.ILink)
class Link(zeit.web.core.view.Content):

    def __call__(self):
        return HTTPMovedPermanently(location=self.context.url)
