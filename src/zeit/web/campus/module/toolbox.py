import logging

import zeit.web
import zeit.web.core.centerpage


log = logging.getLogger(__name__)


@zeit.web.register_module('zco-tool-box')
class Toolbox(zeit.web.core.centerpage.Module):

    def __init__(self, context):
        super(Toolbox, self).__init__(context)
        self.layout = 'toolbox'
