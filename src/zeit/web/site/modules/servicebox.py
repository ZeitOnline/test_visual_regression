import logging

import zeit.web


log = logging.getLogger(__name__)


@zeit.web.register_module('servicebox')
class Servicebox(object):

    def __init__(self):
        pass

    @zeit.web.reify
    def service_items(self):
        pass
