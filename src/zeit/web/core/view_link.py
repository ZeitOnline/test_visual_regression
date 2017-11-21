import pyramid.httpexceptions

import zeit.content.link.interfaces

import zeit.web


@zeit.web.view_config(context=zeit.content.link.interfaces.ILink)
class Link(zeit.web.core.view.Content):

    def __call__(self):
        toggles = zeit.web.core.application.FEATURE_TOGGLES
        url = self.context.url

        if toggles.find('https'):
            url = zeit.web.core.utils.maybe_convert_http_to_https(url)
        return pyramid.httpexceptions.HTTPMovedPermanently(url)
