import logging

import zeit.web.core.block


log = logging.getLogger(__name__)


@zeit.web.register_module('dynamic-cp-header')
class Header(zeit.web.core.block.Module):
    pass
