import functools
import hashlib
import logging
import sys
import types

from dogpile.cache.api import NO_VALUE
import pyramid_dogpile_cache2.cache
import pyramid.threadlocal
import venusian
import zope.component

import zeit.content.cp.interfaces
import zeit.edit.interfaces

import zeit.web.core

__all__ = [
    'reify', 'register_area', 'register_module', 'register_filter',
    'register_ctxfilter', 'register_envfilter', 'register_evalctxfilter',
    'register_global', 'register_ctxfunc', 'register_envfunc',
    'register_evalctxfunc', 'register_test']


log = logging.getLogger(__name__)


def JinjaEnvRegistrator(env_attr, marker=None, category='jinja'):  # NOQA
    """Factory function that returns a decorator configured to register a given
    environment attribute to the jinja context.

    :param str env_attr: Attribute name the returned decorator should register
    :returns: Decorator that registers functions to the jinja context
    :rtype: types.FunctionType
    """
    import zeit.web.core.jinja  # Prevent circular import (zeit.web.__init__)

    def registrator(func):
        """This decorator recronstructs the decorated function and injects
        the safeguarded codeblock into the dynamically created counterpart.

        :internal:
        """
        def callback(scanner, name, obj):
            """Venusian callback that registers the decorated function.

            :internal:
            """
            if not hasattr(scanner, 'env'):
                return

            if isinstance(scanner.env, zeit.web.core.jinja.Environment):
                fn = obj

                @functools.wraps(fn)
                def safeguard(*args, **kw):
                    """Try to execute jinja environment modifier code and
                    intercept potential exceptions. If execution is intercept,
                    return a jinja.Undefined object.

                    :internal:
                    """
                    try:
                        return fn(*args, **kw)
                    except Exception:
                        log.error('Error in jinja modifier %s', func.__name__,
                                  exc_info=True)
                        return zeit.web.core.jinja.Undefined()
                # Unfortunately, wraps doesn't preserve argument defaults
                safeguard.func_defaults = fn.func_defaults

                setattr(sys.modules[fn.__module__], fn.__name__, safeguard)
                obj = safeguard

            if marker and isinstance(obj, types.FunctionType):
                setattr(obj, marker, True)

            if env_attr in scanner.env.__dict__:
                scanner.env.__dict__[env_attr][name] = obj

        venusian.attach(func, callback, category=category)
        return func

    return registrator


# TODO: Implement requestfilter/-global/-test decorators that inject the
#       request as the first argument into the function. Then adapt signature
#       of create_url, get_layout and others in need of a request.

register_filter = JinjaEnvRegistrator('filters')
register_ctxfilter = JinjaEnvRegistrator('filters', 'contextfilter')
register_envfilter = JinjaEnvRegistrator('filters', 'environmentfilter')
register_evalctxfilter = JinjaEnvRegistrator('filters', 'evalcontextfilter')
register_global = JinjaEnvRegistrator('globals')
register_ctxfunc = JinjaEnvRegistrator('globals', 'contextfunction')
register_envfunc = JinjaEnvRegistrator('globals', 'environmentfunction')
register_evalctxfunc = JinjaEnvRegistrator('globals', 'evalcontextfunction')
register_test = JinjaEnvRegistrator('tests')


class NestedAttributeError(StandardError):
    pass


class dont_cache(object):  # NOQA
    """Save the descision that this object is not reify-able."""

    def __init__(self, value):
        self.value = value

    def __call__(self):
        return self.value


class reify(object):  # NOQA
    """Inspired by `pyramid.decorator.reify` and `beaker.cache.cache_region`.

    With this property descriptor you can decorate zero-argument methods
    of view classes, that will become cached read-only attributes.

    The first-level cache will hold the result for the scope of the current
    request only.

    @zeit.web.reify
    def resource_pipeline(self):
        return okay_db.fetch('query')

    You can also specify a dogpile cache region which will act as a
    second-level cache with a configurable ttl. The cache key is derived from
    the `uniqueId` property of the view context.

    @zeit.web.reify('long_term')
    def profile_director(self):
        return slow_api.search('query')

    It is also possible to return a `dont_cache` object and prevent certain
    results from being written to the second-level cache.

    @zeit.web.reify('long_term')
    def system_target(self):
        try:
            return buggy_service.get('query')
        except:
            return zeit.web.dont_cache(fallback)

    """

    def __init__(self, arg):
        if isinstance(arg, basestring):
            # Prevent circular import (zeit.web.__init__)
            import zeit.web.core.cache
            self.cache_region = zeit.web.core.cache.get_region(arg)
            self.func = None
        else:
            self.cache_region = None
            self(arg)

    def __call__(self, func):
        self.func = func
        return self

    def __get__(self, inst, objtype=None):
        if inst is None:
            return self

        l_key = self._local_key(inst)
        g_key = self._global_key(inst)
        cache = self.cache_region

        if l_key is not None:
            try:
                value = getattr(inst, l_key)  # Return from local cache
                g_key = l_key = None
            except AttributeError:
                value = NO_VALUE

        if g_key is not None and value is NO_VALUE and cache is not None:
            value = cache.get(g_key)  # Get from global cache
            if value is not NO_VALUE:
                g_key = None

        if value is NO_VALUE:  # Fetch fresh results
            try:
                value = self.func(inst)
            except AttributeError:
                _, val, tb = sys.exc_info()
                raise NestedAttributeError, val, tb
            except:
                exc, val, tb = sys.exc_info()
                raise exc, val, tb

        if isinstance(value, dont_cache):
            value = value()  # Bypass global cache layer
            g_key = None

        if l_key is not None:
            setattr(inst, l_key, value)  # Write to local cache

        if g_key is not None and cache is not None:
            # XXX We should use cache.get_or_create() instead of get/set,
            # to use the "many readers / one writer" feature of dogpile.cache.
            cache.set(g_key, value)  # Write to global cache

        return value

    def _global_key(self, inst):
        try:
            # XXX I can't decide whether using
            # `self.cache_region.function_key_generator` here instead of
            # hard-coding would be cleaner (because it's not hard-coded and
            # thus potentially customizeable for different regions) or not
            # (because it makes assumptions about the cache region
            # configuration).
            key_generator = pyramid_dogpile_cache2.cache.key_generator(
                None, self.func)
            return key_generator(inst, inst.context.uniqueId)
        except AttributeError:
            return

    def _local_key(self, inst):
        try:
            return self._l_key
        except AttributeError:
            hex_key = hashlib.sha1(self.func.__name__).hexdigest()
            self._l_key = '__{}__'.format(hex_key[:32])
            return self._l_key


def register_module(name):
    """Register a CPExtra implementation for a RAM-style module using the
    cpextra identifier as an adapter name.

    Usage example:
    First, implement your module class in python

    @zeit.web.register_module('ice-cream-truck')
    class IceCreamTruck(zeit.web.core.centerpage.Module):
        @zeit.web.reify
        def flavours(self):
            return ('chocolate', 'vanilla', 'cherry')

    Register the module in the cpextra.xml file, so it's available in vivi

    <cpextra for="zeit.content.cp.interfaces.IArea" id="ice-cream-truck">
        Sell some ice cream on your centerpage!
    </cpextra>

    Create a template in site/templates/inc/module/ice-cream-truck.tpl

    {% for f in module.flavours %}
        <img src="//images.zeit.de/ice-cream-assets/{{ f }}.jpg"/>
    {% endfor %}

    That's it.

    If your module template is self-sufficient, you can even skip the python
    module implementation and registration.
    """
    # Prevent circular import (zeit.web.__init__)
    import zeit.web.core.interfaces

    def registrator(cls):
        gsm = zope.component.getGlobalSiteManager()
        gsm.registerAdapter(cls, (zeit.edit.interfaces.IBlock,),
                            zeit.web.core.interfaces.IBlock, name)
        return cls
    return registrator


def register_area(name):
    """Register an area renderer implementation for a RAM-style area using the
    area kind descriptor as an adapter identifier.
    """

    def registrator(cls):
        gsm = zope.component.getGlobalSiteManager()
        gsm.registerAdapter(cls, (zeit.content.cp.interfaces.IArea,),
                            zeit.content.cp.interfaces.IRenderedArea, name)
        return cls
    return registrator


def cache_on_request(func):
    """Function decorator that caches the function result in a dictionary on
    the pyramid request (attribute is named `_cache_<name>` with the function
    name or the given `cache_name`).

    Note: Only functions without keyword arguments are supported at the moment.
    """
    cache_attribute = '_cache_{}'.format(func.__name__)

    def cached(*args):  # XXX Should we support **kw (if possible)?
        request = pyramid.threadlocal.get_current_request()
        if not request:
            return func(*args)

        try:
            key = hash(args)
        except (NotImplementedError, TypeError), e:
            log.debug(
                'Cannot cache {} for {}: {}'.format(cache_attribute, args, e))
            return func(*args)
        cache = getattr(request, cache_attribute, {})

        if key in cache:
            return cache[key]
        result = func(*args)
        cache[key] = result
        setattr(request, cache_attribute, cache)
        return result
    return cached
