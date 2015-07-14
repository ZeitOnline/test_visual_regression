import itertools
import uuid
import logging

import peak.util.proxies
import grokcore.component
import zope.component

import zeit.cms
import zeit.cms.content.metadata

import zeit.web
import zeit.web.site.area.ranking


log = logging.getLogger(__name__)


SANITY_BOUND = 500


@grokcore.component.adapter(dict)
@grokcore.component.implementer(zeit.cms.interfaces.ICMSContent)
class LazyProxy(object):

    def __init__(self, context, istack=[zeit.cms.interfaces.ICMSContent]):
        def callback():
            factory = context.get('uniqueId', None)
            istack = iter(self.__istack__)
            while True:
                try:
                    iface = next(istack)
                    factory = iface(factory)
                except (StopIteration, TypeError,
                        zope.component.ComponentLookupError):
                    self.__exposed__ = True
                    return factory

        origin = peak.util.proxies.LazyProxy(callback)
        object.__setattr__(self, '__exposed__', False)
        object.__setattr__(self, '__istack__', istack)
        object.__setattr__(self, '__origin__', origin)
        object.__setattr__(self, '__proxy__', context)

    def __getattr__(self, key):
        try:
            return self.__proxy__[key]
        except KeyError:
            return getattr(self.__origin__, key)

    def __setattr__(self, key, value):
        if self.__exposed__:
            setattr(self.__origin__, key, value)
        else:
            # TODO: Properly defer setter until origin is exposed.
            self.__proxy__[key] = value

    def __delattr__(self, key):
        raise NotImplementedError('Sorry, I am too lazy to delete anything.')

    def __hash__(self):
        return hash(self.__origin__)

    def __len__(self):
        return len(self.__origin__)

    def __iter__(self):
        return iter(self.__origin__)

    def __dir__(self):
        return dir(self.__origin__)

    def __conform__(self, iface):
        context = self.__proxy__
        istack = self.__istack__
        return LazyProxy(context, istack + [iface])


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
