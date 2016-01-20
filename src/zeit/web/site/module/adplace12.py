import logging

import zeit.web
import zeit.web.core.module


log = logging.getLogger(__name__)


@zeit.web.register_module('adplace12')
class AdPlace12(zeit.web.core.module.Module):
    pass
