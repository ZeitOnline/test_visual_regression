import lxml.etree

import zeit.web
import zeit.web.site.module


@zeit.web.register_module('xml')
class RawXML(zeit.web.site.module.Module, list):

    @zeit.web.reify
    def xml(self):
        return lxml.etree.tostring(self.context.xml, pretty_print=True)

    @zeit.web.reify
    def alldevices(self):
        return 'alldevices' in self.context.xml.raw.keys()
