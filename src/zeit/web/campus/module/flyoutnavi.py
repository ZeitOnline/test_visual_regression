import zeit.web
import zeit.web.core.centerpage
import zeit.web.campus.navigation


@zeit.web.register_module('zco-flyoutnavi')
class Flyoutnavi(zeit.web.core.centerpage.Module):

    def __init__(self, context):
        super(Flyoutnavi, self).__init__(context)
        self.layout = 'flyoutnavi'
        self.flyoutnavi = zeit.web.campus.navigation.TOOL_FLYOUT_SOURCE
