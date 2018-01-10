import grokcore.component
import zope.component
import zope.interface

import zeit.cms.repository.interfaces
import zeit.cms.repository.repository
import zeit.cms.repository.unknown
import zeit.cms.workingcopy.workingcopy


# Monkey-patches so our content can provide additional marker interfaces

def getitem_with_marker_interface(self, key):
    unique_id = self._get_id_for_name(key)

    __traceback_info__ = (key, unique_id)
    content = self.repository.getUncontainedContent(unique_id)
    # We copied the original method wholesale since calling alsoProvides only
    # once proved to be a significant performance gain,...
    add_marker_interfaces(content)
    # ...and we don't want to locate content here, to keep the performance
    # advantage of dynamic parent lookup.
    return content
zeit.cms.repository.repository.Container.__getitem__ = (
    getitem_with_marker_interface)


def getcontent_with_marker_interface(self, unique_id):
    content = original_getcontent(self, unique_id)
    add_marker_interfaces(content)
    return content
original_getcontent = zeit.cms.repository.repository.Repository.getContent
zeit.cms.repository.repository.Repository.getContent = (
    getcontent_with_marker_interface)


def wc_getitem_with_marker_interface(self, key):
    content = original_wc_getitem(self, key)
    add_marker_interfaces(content, in_repository=False)
    return content
original_wc_getitem = zeit.cms.workingcopy.workingcopy.Workingcopy.__getitem__
zeit.cms.workingcopy.workingcopy.Workingcopy.__getitem__ = (
    wc_getitem_with_marker_interface)


UNKNOWN_RESOURCE_INTERFACES = set(zope.interface.providedBy(
    zeit.cms.repository.unknown.PersistentUnknownResource(u'')))


def add_marker_interfaces(content, in_repository=True):
    # If the meta file is missing, content objects still might provide
    # interfaces like ICommonMetadata or IArticle, while having no contenttype,
    # thereby making any interface-based checks useless. Thus we remove any
    # further interfaces from type-less content objects.
    #
    # Doing this in here instead of a separate step is a performance
    # optimization; the interface provides functions are surprisingly expensive
    if zeit.cms.repository.interfaces.IUnknownResource.providedBy(content):
        zope.interface.directlyProvides(content, *UNKNOWN_RESOURCE_INTERFACES)
    else:
        # required so that DAV properties work. XXX Can we get around this?
        # calling alsoProvides twice is supposed to be somewhat expensive.
        if in_repository:
            zope.interface.alsoProvides(
                content, zeit.cms.repository.interfaces.IRepositoryContent)
        ifaces = []
        for _, result in zope.component.getAdapters(
                (content,),
                zeit.web.core.interfaces.IContentMarkerInterfaces):
            if result:
                ifaces.extend(result)
        zope.interface.alsoProvides(content, *ifaces)


@grokcore.component.adapter(
    zeit.cms.interfaces.ICMSContent, name='internaluse')
@grokcore.component.implementer(
    zeit.web.core.interfaces.IContentMarkerInterfaces)
def mark_everything_interaluse(context):
    return (zeit.web.core.interfaces.IInternalUse,)
