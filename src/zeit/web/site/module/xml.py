import lxml.etree

import zeit.web
import zeit.web.core.centerpage


@zeit.web.register_module('xml')
class RawXML(zeit.web.core.centerpage.Module, list):

    @zeit.web.reify
    def xml(self):
        try:
            xml = self.context.xml.xpath('raw[@alldevices="true"]/*')
            return ''.join(map(lxml.etree.tostring, xml))
        except:
            return ''
