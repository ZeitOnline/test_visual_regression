from pyramid.view import view_config

import zeit.content.cp.interfaces

import zeit.web.core.view


@view_config(context=zeit.content.cp.interfaces.ICenterPage,
             renderer='templates/centerpage.html')
class Centerpage(zeit.web.core.view.Base):
    """Main view class for ZEIT ONLINE centerpages."""

    @zeit.web.reify
    def last_semantic_change(self):
        """Timestamp representing the last semantic change of the centerpage.
        :rtype: datetime.datetime
        """

        return zeit.cms.content.interfaces.ISemanticChange(
            self.context).last_semantic_change
