import zope.component
import zeit.web.site.module


@zeit.web.register_module('zmo-buzzbox')
class Buzzbox(zeit.web.site.module.Module):

    def __init__(self, context):
        super(Buzzbox, self).__init__(context)
        self.layout = 'buzzbox'

    @zeit.web.reify
    def area_buzz(self):
        conn = zope.component.getUtility(zeit.web.core.interfaces.IReach)
        return (
            ('views', conn.get_views(section='zeit-magazin')),
            ('facebook', conn.get_social(
                facet='facebook', section='zeit-magazin')),
            ('comments', conn.get_comments(section='zeit-magazin')))
