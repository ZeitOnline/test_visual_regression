import logging

import zeit.web.core.centerpage


log = logging.getLogger(__name__)


@zeit.web.register_module('centerpage-header')
class Header(zeit.web.core.centerpage.Module):
    pass
