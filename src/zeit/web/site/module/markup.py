import logging

import zeit.web
import zeit.web.site.module


log = logging.getLogger(__name__)


@zeit.web.register_module('markup')
class Markup(zeit.web.site.module.Module, list):

    @zeit.web.reify
    def title(self):
        return self.context.title.strip()

    @zeit.web.reify
    def text(self):
        return self.context.text.strip()
