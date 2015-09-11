import logging

import zeit.web
import zeit.web.site.module


log = logging.getLogger(__name__)


@zeit.web.register_module('adplace12')
class AdPlace12(zeit.web.site.module.Module):
    pass
