import logging

import zeit.web.site.module


log = logging.getLogger(__name__)


@zeit.web.register_module('headerimage')
class HeaderImage(zeit.web.site.module.Module):

    @zeit.web.reify
    def supertitle(self):
        return self.context.supertitle

    @zeit.web.reify
    def title(self):
        return self.context.title

    @zeit.web.reify
    def image(self):
        return self.context.image
