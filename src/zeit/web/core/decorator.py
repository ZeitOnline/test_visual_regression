import logging
import traceback
import sys
import types

import pyramid
import pyramid.decorator
import venusian
import zope.component

import zeit.content.cp.interfaces
import zeit.edit.interfaces

import zeit.web.core.interfaces
import zeit.web.core.jinja


__all__ = [
    'reify', 'register_copyrights', 'register_area', 'register_module',
    'register_filter', 'register_ctxfilter', 'register_envfilter',
    'register_evalctxfilter', 'register_global', 'register_ctxfunc',
    'register_envfunc', 'register_evalctxfunc', 'register_test',
]


log = logging.getLogger(__name__)


def safeguard(*args, **kw):
    """Try to execute jinja environment modifier code and intercept potential
    exceptions. If execution is intercept, return a jinja.Undefined object.

    :internal:
    """
    try:
        return globals()['func'](*args, **kw)
    except BaseException:
        logger(*sys.exc_info())
        return globals()['undefined']()


def logger(exc, val, tb):
    """Log an exception that occoured during a jinja env modifier to
    the error level of this module's logger. Strips off the uppermost
    entry of the traceback.

    :internal:
    """
    log.error(u''.join(
        ['Traceback (most recent call last):\n'] +
        traceback.format_list(traceback.extract_tb(tb)[1:]) +
        [exc.__name__, ': ', unicode(val)]))


def JinjaEnvRegistrator(env_attr, marker=None, category='jinja'):  # NOQA
    """Factory function that returns a decorator configured to register a given
    environment attribute to the jinja context.

    :param str env_attr: Attribute name the returned decorator should register
    :returns: Decorator that registers functions to the jinja context
    :rtype: types.FunctionType
    """
    def registrator(func):
        """This decorator recronstructs the decorated function and injects
        the safeguarded codeblock into the dynamically created counterpart.

        :internal:
        """
        def callback(scanner, name, obj):
            """Venusian callback that registers the decorated function.

            :internal:
            """
            if not zope.component.getUtility(
                    zeit.web.core.interfaces.ISettings).get(
                        'debug.propagate_jinja_errors', False):

                fn = types.FunctionType(
                    safeguard.func_code, obj.func_globals.copy(),
                    obj.func_name, obj.func_defaults, obj.func_closure)

                fn.func_globals.update({
                    'func': obj, 'logger': logger, 'sys': sys,
                    'undefined': zeit.web.core.jinja.Undefined})

                fn.__doc__ = obj.__doc__

                setattr(sys.modules[obj.__module__], obj.func_name, fn)
                obj = fn

            if marker and isinstance(obj, types.FunctionType):
                setattr(obj, marker, True)

            if hasattr(scanner, 'env') and env_attr in scanner.env.__dict__:
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


def register_copyrights(func):
    """A decorator that registers all teaser image copyrights it finds in the
    teaser container the decorated method (or property) returns.
    """
    def wrapped(self):
        container = func(self)
        if container:
            for t in zeit.web.core.interfaces.ITeaserSequence(container):
                if t.image:
                    self._copyrights.setdefault(t.image.image_group, t.image)
        return container
    return wrapped


class NestedAttributeError(StandardError):
    pass


class reify(pyramid.decorator.reify):  # NOQA
    """Subclass of `pyramid.decorator.reify` that fixes misleading tracebacks
    caused by AttributeErrors nested inside the property code."""

    def __get__(self, *args, **kw):
        try:
            return super(reify, self).__get__(*args, **kw)
        except AttributeError:
            _, val, tb = sys.exc_info()
            raise NestedAttributeError, val, tb
        except:
            exc, val, tb = sys.exc_info()
            raise exc, val, tb


def register_module(name):
    """Register a CPExtra implementation for a RAM-style module using the
    cpextra identifier as an adapter name.

    Usage example:
    First, implement your module class in python

    @zeit.web.register_module('ice-cream-truck')
    class IceCreamTruck(zeit.web.site.module.Module):
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
    """

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
