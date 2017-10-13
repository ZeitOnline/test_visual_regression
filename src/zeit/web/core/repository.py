import os.path

import grokcore.component
import zope.component
import zope.interface

import zeit.cms.content.xmlsupport
import zeit.cms.repository.file
import zeit.cms.repository.folder
import zeit.cms.repository.unknown


# Monkey-patch so our content can provide additional marker interfaces
def getitem_with_marker_interface(self, key):
    unique_id = self._get_id_for_name(key)

    __traceback_info__ = (key, unique_id)
    content = self.repository.getUncontainedContent(unique_id)
    # We copied the original method wholesale since calling alsoProvides only
    # once proved to be a significant performance gain,...
    _add_marker_interfaces(content)
    # ...and we don't want to locate content here, due to resolve_parent below.
    return content
zeit.cms.repository.repository.Container.__getitem__ = (
    getitem_with_marker_interface)


# Performance optimization: Instead of traversing to the target object (and
# thus instantiating all the folders in between), resolve it directly via the
# connector, if possible. Notable exceptions include variant images and dynamic
# folders, those are retried the traditional way.
# NOTE: We cannot locate the content object here, since not materializing the
# __parent__ folder is kind of the point. Thus, ``resolve_parent`` below.
def getcontent_try_without_traversal(self, unique_id):
    try:
        content = self.getUncontainedContent(unique_id)
    except KeyError:
        content = original_getcontent(self, unique_id)
    _add_marker_interfaces(content)
    return content
original_getcontent = zeit.cms.repository.repository.Repository.getContent
zeit.cms.repository.repository.Repository.getContent = (
    getcontent_try_without_traversal)


UNKNOWN_RESOURCE_INTERFACES = set(zope.interface.providedBy(
    zeit.cms.repository.unknown.PersistentUnknownResource(u'')))


def _add_marker_interfaces(content):
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


# Determine __parent__ folder on access, instead of having Repository write it.
def resolve_parent(self):
    workingcopy_parent = getattr(self, '_v_workingcopy_parent', None)
    if workingcopy_parent is not None:
        return workingcopy_parent

    unique_id = self.uniqueId
    trailing_slash = unique_id.endswith('/')
    if trailing_slash:
        unique_id = unique_id[:-1]
    parent_id = os.path.dirname(unique_id)
    parent_id = parent_id.rstrip('/') + '/'
    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)
    return original_getcontent(repository, parent_id)


# For checkout (which we use in tests) the parent must be settable.
def set_workingcopy_parent(self, value):
    self._v_workingcopy_parent = value

# XXX Patching all possible content base-classes is a bit of guesswork.
zeit.cms.content.xmlsupport.XMLContentBase.__parent__ = property(
    resolve_parent, set_workingcopy_parent)
zeit.cms.repository.file.RepositoryFile.__parent__ = property(
    resolve_parent, set_workingcopy_parent)
zeit.cms.repository.folder.Folder.__parent__ = property(
    resolve_parent, set_workingcopy_parent)
