import urlparse

import grokcore.component as grok
import zope.component
import zope.interface

import zeit.arbeit.interfaces
import zeit.campus.interfaces
import zeit.cms.interfaces
import zeit.magazin.interfaces

import zeit.web.core.interfaces


@grok.adapter(zope.interface.Interface)
@grok.implementer(zeit.web.core.interfaces.IVertical)
def default_vertical(context):
    return ''


@grok.adapter(zeit.cms.interfaces.ICMSContent)
@grok.implementer(zeit.web.core.interfaces.IVertical)
def zon_vertical(context):
    return 'zon'


@grok.adapter(zeit.magazin.interfaces.IZMOContent)
@grok.implementer(zeit.web.core.interfaces.IVertical)
def zmo_vertical(context):
    # XXX Stopgap until longforms are not IZMOContent anymore (ZON-2411).
    if urlparse.urlparse(context.uniqueId).path.startswith('/feature'):
        return 'zon'
    return 'zmo'


# We might think about adding the identifer as a tagged value to the respective
# interfaces, and then retrieve it by looking for interfaces provided by the
# content object that inherit from ISectionMarker.
@grok.adapter(zeit.campus.interfaces.IZCOContent)
@grok.implementer(zeit.web.core.interfaces.IVertical)
def zco_vertical(context):
    return 'zco'


@grok.adapter(zeit.arbeit.interfaces.IZARContent)
@grok.implementer(zeit.web.core.interfaces.IVertical)
def zar_vertical(context):
    return 'zar'
