import zeit.web
import zeit.web.core.centerpage


@zeit.web.register_module('zco-tool-box')
class Toolbox(zeit.web.core.centerpage.Module):

    def __init__(self, context):
        super(Toolbox, self).__init__(context)
        self.layout = 'toolbox'
        self.toolbox = TOOL_SOURCE


class ToolSource(zeit.cms.content.sources.SimpleXMLSourceBase):

    product_configuration = 'zeit.web'
    config_url = 'zco-toolbox-source'

    def __iter__(self):
        tree = self._get_tree()
        for node in tree.iterchildren('link'):
            yield dict(title=unicode(node.get('title')),
                       href_title=unicode(node.get('href_title')),
                       text=unicode(node.get('text')),
                       cta=unicode(node.get('cta')),
                       href=unicode(node.get('href')))

    @property
    def footer_text(self):
        tree = self._get_tree()
        return tree.get('footer')

    @property
    def header_text(self):
        tree = self._get_tree()
        return tree.get('header')

    @property
    def footer_link(self):
        tree = self._get_tree()
        return tree.get('href')

TOOL_SOURCE = ToolSource()
