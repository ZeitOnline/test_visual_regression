import zeit.web
import zeit.web.core.centerpage


@zeit.web.register_module('zco-tool-box')
class Toolbox(zeit.web.core.centerpage.Module):

    def __init__(self, context):
        super(Toolbox, self).__init__(context)
        self.layout = 'toolbox'

        services = zeit.web.campus.module.toolbox.ToolSource(
            'centerpage-toolbox-source')


class ToolSource(zeit.cms.content.sources.SimpleXMLSourceBase):

    product_configuration = 'zeit.web'

    def __init__(self, config_url):
        self.config_url = config_url

    def __iter__(self):
        tree = self._get_tree()
        for column in tree.iterchildren('column'):
            yield [Service(unicode(service.get('id')),
                           unicode(service.text.strip()),
                           unicode(service.get('href')))
                   for service in column.iterchildren('*')]
