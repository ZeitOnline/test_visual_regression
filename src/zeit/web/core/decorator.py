import sys

import pyramid
import pyramid.decorator
import venusian
import zope.component

import zeit.content.cp.interfaces
import zeit.edit.interfaces

import zeit.web.core.interfaces


def JinjaEnvRegistrator(env_attr):
    """Factory function that returns a decorator configured to register a given
    environment attribute to the jinja context.

    :param str env_attr: Attribute name the returned decorator should register
    :returns: Decorator that registers functions to the jinja context
    :rtype: types.FunctionType
    """
    def registrator(func):
        """This decorator is non-destructive, meaning it does not replace the
        decorated function with a wrapped one. Instead, a callback is attached
        to the venusian scanner that is triggered at application startup.

        :internal:
        """
        def callback(scanner, name, obj):
            """Venusian callback that registers the decorated function under
            its `func_name` to the jinja `env_attr` passed to the registrator
            factory.

            :internal:
            """
            if hasattr(scanner, 'env') and env_attr in scanner.env.__dict__:
                scanner.env.__dict__[env_attr][name] = obj
        venusian.attach(func, callback, category='jinja')
        return func
    return registrator


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


class reify(pyramid.decorator.reify):
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
    cpextra name as an adapter identifier.

    Usage example:
    First, implement your module class in python

    @zeit.web.register_module('ice-cream-truck')
    class IceCreamTruck(object):
        @zeit.web.reify
        def flavours(self):
            return ('chocolate', 'vanilla', 'cherry')

    Register the module in the cpextra.xml file, so it's available in vivi

    <cpextra for="zeit.content.cp.interfaces.IArea" id="ice-cream-truck">
        Sell some ice cream on your centerpage!
    </cpextra>

    Create a template in site/templates/inc/modules/ice-cream-truck.tpl

    {% for f in module.flavours %}
        <img src="//images.zeit.de/ice-cream-assets/{{ f }}.jpg"/>
    {% endfor %}

    That's it.
    """

    def registrator(cls):
        gsm = zope.component.getGlobalSiteManager()
        gsm.registerAdapter(cls, (zeit.content.cp.interfaces.ICPExtraBlock,),
                            zeit.edit.interfaces.IBlock, name)
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
