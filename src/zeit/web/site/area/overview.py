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


SANITY_BOUND = 500

_get, _set = object.__getattribute__, object.__setattr__


@grokcore.component.adapter(dict)
@grokcore.component.implementer(zeit.cms.interfaces.ICMSContent)
class LazyProxy(object):

    def __init__(self, context, istack=[zeit.cms.interfaces.ICMSContent]):
        def callback():
            _set(self, '__exposed__', True)
            factory = context.get('uniqueId', None)
            istack = iter(_get(self, '__istack__'))
            while True:
                try:
                    iface = next(istack)
                    factory = iface(factory)
                except (StopIteration, TypeError):
                    return factory

        origin = peak.util.proxies.LazyProxy(callback)
        _set(self, '__proxy__', context)
        _set(self, '__origin__', origin)
        _set(self, '__exposed__', False)
        _set(self, '__istack__', istack)

    def __getattr__(self, key):
        try:
            return _get(self, '__proxy__')[key]
        except KeyError:
            return getattr(_get(self, '__origin__'), key)

    def __setattr__(self, key, value):
        if self.__exposed__:
            setattr(_get(self, '__origin__'), key, value)
        else:
            # TODO: Properly defer setting until origin is exposed.
            _get(self, '__proxy__')[key] = value

    def __delattr__(self, key):
        raise NotImplementedError('I\'m too lazy to delete anything.')

    def __dir__(self):
        return dir(zeit.cms.content.metadata.CommonMetadata)

    def __conform__(self, iface):
        context = _get(self, '__proxy__')
        istack = _get(self, '__istack__')
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
