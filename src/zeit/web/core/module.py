# python package
#
import pyramid.threadlocal
import zope.interface

import zeit.content.cp.interfaces
import zeit.content.cp.layout
import zeit.edit.interfaces


class Module(object):
    """Base class for RAM-style modules to be used in cp2015 centerpages.

    See `zeit.web.core.decorator.register_module` for doc and example.
    """

    zope.interface.implements(zeit.edit.interfaces.IBlock)

    __parent__ = NotImplemented

    def __init__(self, context):
        self.context = context
        if zeit.content.cp.interfaces.ICPExtraBlock.providedBy(context):
            self.layout = context.cpextra
        elif zeit.edit.interfaces.IBlock.providedBy(context):
            self.layout = context.type

    def __hash__(self):
        return self.context.xml.attrib.get(
            '{http://namespaces.zeit.de/CMS/cp}__name__',
            super(Module, self)).__hash__()

    def __repr__(self):
        return object.__repr__(self)

    @property
    def layout(self):
        return getattr(self, '_layout', None)

    @layout.setter
    def layout(self, value):
        self._layout = zeit.content.cp.layout.BlockLayout(
            value, value, areas=[], image_pattern=value)

    @property
    def request(self):
        # XXX Yes, yes, it's bad practice. But milking the request object
        #     during traversal is ever so slightly more horrible. (ND)
        return pyramid.threadlocal.get_current_request()
