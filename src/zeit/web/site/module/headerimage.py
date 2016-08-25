import logging

import grokcore.component

import zeit.content.image.interfaces

import zeit.web.core.centerpage


log = logging.getLogger(__name__)


@zeit.web.register_module('headerimage')
class HeaderImage(zeit.web.core.centerpage.Module):

    @zeit.web.reify
    def supertitle(self):
        return self.context.supertitle

    @zeit.web.reify
    def title(self):
        return self.context.title

    @zeit.web.reify
    def image(self):
        return self.context.image

    @zeit.web.reify
    def animate(self):
        return getattr(self.context, 'animate', False)


@grokcore.component.implementer(zeit.content.image.interfaces.IImages)
@grokcore.component.adapter(HeaderImage)
class HeaderImageImages(object):

    fill_color = None

    def __init__(self, context):
        self.context = context
        self.image = context.image
