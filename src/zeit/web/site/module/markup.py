import logging

import zeit.web
import zeit.web.core.module


log = logging.getLogger(__name__)


@zeit.web.register_module('markup')
class Markup(zeit.web.core.module.Module, list):

    @zeit.web.reify
    def title(self):
        if self.context.title is not None:
            return self.context.title.strip()

    @zeit.web.reify
    def text(self):
        if self.context.text is not None:
            return self.context.text.strip()
