import logging

import zeit.web
import zeit.web.core.centerpage


log = logging.getLogger(__name__)


@zeit.web.register_module('adplace13')
class AdPlace13(zeit.web.core.centerpage.Module):
    pass
