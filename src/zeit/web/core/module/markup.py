import logging
import zeit.web.core.block

import zeit.web
import zeit.web.core.centerpage
import lxml.etree


log = logging.getLogger(__name__)


@zeit.web.register_module('markup')
class Markup(zeit.web.core.centerpage.Module, list):

    @zeit.web.reify
    def title(self):
        if self.context.title is not None:
            return self.context.title.strip()

    @zeit.web.reify
    def text(self):
        if self.context.text is not None:
            return self.maybe_convert_text(self.context.text)

    def maybe_convert_text(self, text):
        toggles = zeit.web.core.application.FEATURE_TOGGLES
        if not toggles.find('https'):
            return text
        xml = lxml.etree.fromstring(self.context.text)
        for link in xml.xpath('//a'):
            if link.get('href'):
                link.set('href',
                         zeit.web.core.block.maybe_convert_http_to_https(
                            link.get('href')))
        return lxml.etree.tostring(xml)
