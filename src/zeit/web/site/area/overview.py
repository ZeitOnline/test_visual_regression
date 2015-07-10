import itertools
import uuid
import logging

import peak.util.proxies
import grokcore.component

import zeit.cms
import zeit.cms.content.metadata

import zeit.web
import zeit.web.site.area.ranking


log = logging.getLogger(__name__)


SANITY_BOUND = 10


@grokcore.component.adapter(dict)
@grokcore.component.implementer(zeit.cms.interfaces.ICMSContent)
class ContentProxy(object):

    def __init__(self, context):
        def callback():
            object.__setattr__(self, '__exposed__', True)
            unique_id = context.get('uniqueId', None)
            return zeit.cms.interfaces.ICMSContent(unique_id, None)

        proxy = peak.util.proxies.LazyProxy(callback)
        object.__setattr__(self, '__proxy__', context)
        object.__setattr__(self, '__origin__', proxy)
        object.__setattr__(self, '__exposed__', False)

    def __getattr__(self, key):
        try:
            return object.__getattribute__(self, '__proxy__')[key]
        except KeyError:
            return getattr(object.__getattribute__(self, '__origin__'), key)

    def __setattr__(self, key, value):
        if self.__exposed__:
            setattr(object.__getattribute__(self, '__origin__'), key, value)
        else:
            object.__getattribute__(self, '__proxy__')[key] = value

    def __delattr__(self, key):
        raise NotImplementedError('I\'m too lazy to delete anything.')

    def __dir__(self):
        return dir(zeit.cms.content.metadata.CommonMetadata)


@zeit.web.register_area('overview')
class Overview(zeit.web.site.area.ranking.Ranking):

    count = SANITY_BOUND

    @property
    def placeholder(self):
        values = self.context.values()
        length = len(values)
        if not length or self.hits <= length:
            return iter(values)
        overhang = min(self.hits, SANITY_BOUND) - length
        clones = self.clone_factory(values[-1], overhang)
        return itertools.chain(values, clones)

    @staticmethod
    def clone_factory(jango, count):
        for _ in range(count):
            clone = type(jango)(jango.__parent__, jango.xml)
            clone.__name__ = str(uuid.uuid4())
            yield clone
