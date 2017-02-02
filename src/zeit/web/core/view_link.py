import pyramid.httpexceptions

import zeit.content.link.interfaces

import zeit.web


@zeit.web.view_config(context=zeit.content.link.interfaces.ILink)
class Link(zeit.web.core.view.Content):

    def __call__(self):
        return pyramid.httpexceptions.HTTPMovedPermanently(self.context.url)
