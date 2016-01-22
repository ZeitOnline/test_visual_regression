import logging

import zeit.web
import zeit.web.core.centerpage


log = logging.getLogger(__name__)


@zeit.web.register_module('adplace12')
class AdPlace12(zeit.web.core.centerpage.Module):
    pass
