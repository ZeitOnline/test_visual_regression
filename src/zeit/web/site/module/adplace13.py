import logging

import zeit.web
import zeit.web.site.module


log = logging.getLogger(__name__)


@zeit.web.register_module('adplace13')
class AdPlace13(zeit.web.site.module.Module):
    pass
