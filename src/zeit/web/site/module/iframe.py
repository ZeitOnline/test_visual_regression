import logging

import zeit.web.site.module


log = logging.getLogger(__name__)


@zeit.web.register_module('iframe')
class IFrame(zeit.web.site.module.Module):

    @zeit.web.reify
    def src(self):
        return self.context.url
