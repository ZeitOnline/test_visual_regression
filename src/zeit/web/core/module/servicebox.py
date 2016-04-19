import zope.security.proxy

import zeit.cms.content.sources


class Service(object):

    def __init__(self, id=None, title=None, href=None):
        self.id = id
        self.title = title
        self.href = href

    def __eq__(self, other):
        if not zope.security.proxy.isinstance(other, self.__class__):
            return False
        return self.id == other.id


class ServiceSource(zeit.cms.content.sources.SimpleContextualXMLSource):

    product_configuration = 'zeit.web'

    def __init__(self, config_url):
        self.config_url = config_url

    def getValues(self, context):
        tree = self._get_tree()
        return [Service(unicode(node.get('id')),
                        unicode(node.text.strip()),
                        unicode(node.get('href')))
                for node in tree.iterchildren('*')]

    def getTitle(self, context, value):
        return value.title

    def getToken(self, context, value):
        return super(ServiceSource, self).getToken(context, value.id)


class Servicebox(zeit.web.core.centerpage.Module):

    services = NotImplemented
    items_per_column = NotImplemented
    title = NotImplemented

    @zeit.web.reify
    def service_items(self):
        items = list(self.services(self))
        return list(items[x:x + self.items_per_column]
                    for x in xrange(0, len(items), self.items_per_column))
