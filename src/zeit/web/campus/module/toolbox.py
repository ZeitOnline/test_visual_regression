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
                       title_flyout=unicode(node.get('title_flyout')),
                       text=unicode(node.get('text')),
                       cta=unicode(node.get('cta')),
                       cta_flyout=unicode(node.get('cta_flyout')),
                       tracking=unicode(node.get('tracking')),
                       href=unicode(node.get('href')))

    @property
    def header_text(self):
        tree = self._get_tree()
        return tree.get('header')

    @property
    def footer_text(self):
        tree = self._get_tree()
        return tree.get('footer')

    @property
    def footer_link(self):
        tree = self._get_tree()
        return tree.get('href')

    @property
    def footer_tracking(self):
        tree = self._get_tree()
        return tree.get('tracking')

TOOL_SOURCE = ToolSource()
