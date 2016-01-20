import logging

import zeit.web.core.module


log = logging.getLogger(__name__)


@zeit.web.register_module('centerpage-header')
class Header(zeit.web.core.module.Module):
    pass
