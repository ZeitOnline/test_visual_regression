import logging

import zope.security.proxy

import zeit.cms.content.sources

import zeit.web


log = logging.getLogger(__name__)


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

    config_url = 'source-servicebox'

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


@zeit.web.register_module('servicebox')
class Servicebox(object):

    service_source = ServiceSource()

    @zeit.web.reify
    def service_items(self):
        self.service_source
