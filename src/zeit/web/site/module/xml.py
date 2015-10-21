import lxml.etree

import zeit.web
import zeit.web.site.module


@zeit.web.register_module('xml')
class RawXML(zeit.web.site.module.Module, list):

    @zeit.web.reify
    def xml(self):
        try:
            xml = self.context.xml.find('raw[@alldevices="true"]/*')
            return ''.join(map(lxml.etree.tostring, xml))
        except:
            return ''
