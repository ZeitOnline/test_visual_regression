import logging

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
        return self.context.animate
