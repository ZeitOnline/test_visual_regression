from lxml import etree
from pyramid.view import view_config

import zeit.content.cp.interfaces
import zeit.frontend.view
import zeit.content.cp.area


@view_config(context=zeit.content.cp.area.Lead, renderer='string')
class XMLView(zeit.frontend.view.Base):

    def __call__(self):
        lead = zeit.content.cp.interfaces.IAutomaticRegion(self.context)
        return etree.tostring(lead.rendered_xml, pretty_print=True)
