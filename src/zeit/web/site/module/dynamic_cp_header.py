import logging

import zeit.web.site.module


log = logging.getLogger(__name__)


@zeit.web.register_module('dynamic-cp-header')
class Header(zeit.web.site.module.Module):
    pass
