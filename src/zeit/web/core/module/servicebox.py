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


class ServiceSource(zeit.cms.content.sources.SimpleXMLSourceBase):

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


class Servicebox(zeit.web.core.centerpage.Module):

    source = NotImplemented
    title = NotImplemented

    @zeit.web.reify
    def services(self):
        return iter(self.source)
