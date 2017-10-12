import os.path

import zope.component
import zope.interface

import zeit.cms.content.xmlsupport
import zeit.cms.repository.file
import zeit.cms.repository.folder
import zeit.cms.repository.unknown


# Monkey-patch so our content provides a marker interface,
# thus Source entries can be ``available`` only for zeit.web, but not vivi.
def getitem_with_marker_interface(self, key):
    unique_id = self._get_id_for_name(key)

    __traceback_info__ = (key, unique_id)
    content = self.repository.getUncontainedContent(unique_id)
    # We copied the original method wholesale since calling alsoProvides only
    # once proved to be a significant performance gain,...
    zope.interface.alsoProvides(
        content,
        zeit.cms.repository.interfaces.IRepositoryContent,
        zeit.web.core.interfaces.IInternalUse)
    _remove_misleading_interfaces(content)
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
    zope.interface.alsoProvides(
        content, zeit.cms.repository.interfaces.IRepositoryContent,
        zeit.web.core.interfaces.IInternalUse)
    _remove_misleading_interfaces(content)
    return content
original_getcontent = zeit.cms.repository.repository.Repository.getContent
zeit.cms.repository.repository.Repository.getContent = (
    getcontent_try_without_traversal)


UNKNOWN_RESOURCE_INTERFACES = set(zope.interface.providedBy(
    zeit.cms.repository.unknown.PersistentUnknownResource(u'')))


def _remove_misleading_interfaces(content):
    """If the meta file is missing, content objects still might provide
    interfaces like ICommonMetadata or IArticle, while having no content-type,
    thereby making any interface-based checks useless. Thus we remove any
    further interfaces from type-less content objects.
    """
    if zeit.cms.repository.interfaces.IUnknownResource.providedBy(content):
        zope.interface.directlyProvides(content, *UNKNOWN_RESOURCE_INTERFACES)


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
