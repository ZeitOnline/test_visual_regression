import logging

import zeit.web.core.module


log = logging.getLogger(__name__)


@zeit.web.register_module('frame')
class Frame(zeit.web.core.module.Module):

    @zeit.web.reify
    def src(self):
        return self.context.url

    @zeit.web.reify
    def title(self):
        return self.context.title
