import logging
import re
import urlparse

import grokcore.component
import pyramid.httpexceptions
import pyramid.interfaces
import pyramid.traversal
import pyramid.urldispatch
import zc.sourcefactory.source
import zope.component
import zope.interface

import zeit.cms.repository.interfaces
import zeit.cms.repository.folder
import zeit.cms.repository.repository
import zeit.content.gallery.interfaces
import zeit.content.article.interfaces
import zeit.content.cp.interfaces
import zeit.content.dynamicfolder.interfaces
import zeit.content.video.interfaces

import zeit.web.core.article
import zeit.web.core.interfaces
import zeit.web.core.template
import zeit.web.core.utils
import zeit.web.magazin.article


log = logging.getLogger(__name__)
CONFIG_CACHE = zeit.web.core.cache.get_region('config')


def traverser(*required):
    def registrator(factory):
        gsm = zope.component.getGlobalSiteManager()
        gsm.registerSubscriptionAdapter(
            factory, required, zeit.web.core.interfaces.ITraversable)
        return factory
    return registrator


class Traversable(object):

    def __init__(self, context):
        self.context = context


class Retraverse(Exception):

    def __init__(self, request):
        log.debug(u'Retraversing {}'.format(request.path))


@grokcore.component.adapter(zeit.cms.repository.interfaces.IRepository)
@grokcore.component.implementer(pyramid.interfaces.ITraverser)
class RepositoryTraverser(pyramid.traversal.ResourceTreeTraverser):

    def __call__(self, request):
        if request.path_info.startswith(u'/wcpreview'):
            # wosc: Changing request.path_info is kludgy, but I haven't found a
            # cleaner way to get the traversal mechanism to do what I want.
            request.path_info = request.path_info.replace(
                u'/wcpreview', u'', 1)
            self.root = zope.component.getUtility(
                zeit.cms.workingcopy.interfaces.IWorkingcopyLocation)
            tdict = super(RepositoryTraverser, self).__call__(request)
            tdict['traversed'] = (u'wcpreview',) + tdict['traversed']
            request.path_info = u'/wcpreview' + request.path_info
        else:
            tdict = super(RepositoryTraverser, self).__call__(request)

        return self.invoke(request=request, **tdict)

    @classmethod
    def invoke(cls, **tdict):
        for sub in zope.component.subscribers(
                [tdict.get('context')], zeit.web.core.interfaces.ITraversable):
            try:
                sub(tdict)
            except Retraverse:
                return cls.invoke(**tdict)
        return tdict


@traverser(zeit.content.gallery.interfaces.IGallery)
class Gallery(Traversable):

    def __call__(self, tdict):
        if tdict['view_name'].startswith('seite') and not tdict['subpath']:
            raise pyramid.httpexceptions.HTTPMovedPermanently(
                location=urlparse.urlparse(self.context.uniqueId).path)


@traverser(zeit.content.article.interfaces.IArticle)
class Article(Traversable):

    def __call__(self, tdict):
        if tdict['view_name'].startswith('seite') and not tdict['subpath']:
            tdict['view_name'] = 'seite'

        if tdict['view_name'] == 'module':
            tdict['context'] = self.context.body
            tdict['traversed'] += (tdict['view_name'],)
            tdict['view_name'] = ''
            raise Retraverse(tdict['request'])


@traverser(zeit.content.article.edit.interfaces.IEditableBody)
class ArticleBody(Traversable):

    def __call__(self, tdict):
        try:
            tdict['context'] = self.context[tdict['subpath'][0]]
        except (IndexError, KeyError, TypeError):
            pass
        else:
            tdict['traversed'] += (tdict['subpath'][0],)
            tdict['subpath'] = tdict['subpath'][1:]
            if len(tdict['subpath']) == 1:
                tdict['view_name'] = tdict['subpath'][0]
                tdict['subpath'] = ()


@traverser(zeit.content.cp.interfaces.ICenterPage)
class CenterPage2015(Traversable):

    def __call__(self, tdict):
        # XXX Ugly workaround until the "new world" content is up to date.
        if tdict['view_name'] in ['rss-spektrum-flavoured', 'xml']:
            return

        try:
            name = u'{}.cp2015'.format(tdict['context'].__name__)
            assert name != tdict['context'].__name__
            pos = tdict['traversed'].index(tdict['context'].__name__)
            tdict['context'] = tdict['context'].__parent__[name]
        except (AssertionError, KeyError, TypeError, ValueError):
            pass
        else:
            travd = tdict['traversed']
            tdict['traversed'] = travd[:pos] + (name,) + travd[pos + 1:]
            raise Retraverse(tdict['request'])


@traverser(zeit.content.cp.interfaces.ICenterPage)
class CenterpageArea(Traversable):

    def __call__(self, tdict):
        if tdict['view_name'] != 'area':
            return

        name = tdict['subpath'][0]

        def uid_cond(index, area):
            return area.uniqueId.rsplit('/', 1)[-1] == name

        def index_cond(index, area):
            try:
                return index == int(name.lstrip(u'no-'))
            except ValueError:
                raise pyramid.httpexceptions.HTTPNotFound('Area not found')

        if name.startswith('id-'):
            condition = uid_cond
        elif name.startswith('no-'):
            condition = index_cond
        else:
            raise pyramid.httpexceptions.HTTPNotFound('Area not found')

        index = 1
        found = None
        for region in self.context.values():
            for area in region.values():
                if condition(index, area):
                    found = area
                    break
                else:
                    index += 1
            if found is not None:
                break
        if found is None:
            raise pyramid.httpexceptions.HTTPNotFound('Area not found')

        tdict['context'] = zeit.web.core.centerpage.get_area(found)
        tdict['traversed'] += (tdict['view_name'], tdict['subpath'][0])
        tdict['subpath'] = tdict['subpath'][1:]
        if len(tdict['subpath']) == 1:
            tdict['view_name'] = tdict['subpath'][0]
            tdict['subpath'] = ()
        else:
            tdict['view_name'] = ''


@traverser(zeit.cms.repository.interfaces.IFolder)
class Folder(Traversable):

    def __call__(self, tdict):
        """Redirect traversed folders to a location suffixed by `/index`."""
        if tdict['view_name']:
            # We're not at the end of the URL yet.
            return
        if getattr(tdict['request'].matched_route, 'name', '') == 'home' or (
                type(tdict['context']) == zeit.cms.repository.folder.Folder):
            url = zeit.web.core.utils.update_path(
                tdict['request'].url, tdict['request'].path, 'index')
            raise pyramid.httpexceptions.HTTPMovedPermanently(location=url)


@traverser(zeit.cms.repository.interfaces.IRepository)  # '/' is the repository
class RootFolder(Traversable):
    def __call__(self, tdict):
        """Redirect the repository root to a location suffixed by `/index`."""
        if tdict['view_name'] or tdict['request'].matched_route:
            # We're not at the end of the URL yet.
            return
        url = zeit.web.core.utils.update_path(
            tdict['request'].url, tdict['request'].path, 'index')
        raise pyramid.httpexceptions.HTTPMovedPermanently(location=url)


@traverser(zeit.content.dynamicfolder.interfaces.IRepositoryDynamicFolder)
class DynamicFolder(Traversable):

    def __call__(self, tdict):
        if not tdict['view_name']:
            url = zeit.web.core.utils.update_path(
                tdict['request'].url, tdict['request'].path, 'index')
            raise pyramid.httpexceptions.HTTPMovedPermanently(location=url)
        try:
            tdict['context'] = self.context[tdict['view_name']]
        except (IndexError, KeyError, TypeError):
            pass
        else:
            tdict['traversed'] += (tdict['view_name'],)
            tdict['view_name'] = ''
            raise Retraverse(tdict['request'])


@traverser(zeit.content.video.interfaces.IVideo)
class Video(Traversable):

    def __call__(self, tdict):
        # Internal details how views are registered are taken from
        # pyramid.config.views.add_view().
        request = tdict['request']
        request_iface = pyramid.interfaces.IRequest
        if request.matched_route:
            request_iface = request.registry.getUtility(
                pyramid.interfaces.IRouteRequest,
                name=request.matched_route.name)
        view_names = [
            name for name, factory in request.registry.adapters.lookupAll((
                pyramid.interfaces.IViewClassifier,
                request_iface,
                zope.interface.providedBy(tdict['context'])
            ), pyramid.interfaces.IView) if name]
        # XXX We assume no video will ever have e.g. `comment-form` as its slug
        if tdict['view_name'] not in view_names:
            tdict['request'].headers['X-SEO-Slug'] = tdict['view_name']
            tdict['view_name'] = ''


class HostRestrictionPredicate(object):
    """Requests with a specific host header shall be exclusively answered by
    certain views. This means, that these views can only be accessed with that
    host header and all other views shall not answer if the header is present.

    The predicate is used like following:

      @zeit.web.view_config(context=IFoo, host_restriction=True)
      class FooView(object):
          ...

      @zeit.web.view_config(context=IFooBar, host_restriction='bar')
      class FooBarView(FooView)
          ...

    Our foo view is now configured to be available under abc.zeit.de,
    xyz.zeit.de and any other host name, that is not bar.zeit.de (!).

    Whereas the foobar view is exclusively (!) available with a host header
    of bar.zeit.de.

    Accepted value types:

    True    view available for all host-headers unclaimed by other views
    False   view unaffected by host-header restrictions
    str     singular host-header restriction
    tuple   multiple host-headers

    Note: Headers may also contain a staging segment, i.e. xml.staging.zeit.de
    """

    def __init__(self, value, config):
        if value in (None, True, False):
            self.value = bool(value)
            return
        elif isinstance(value, basestring):
            self.value = (value,)  # Ensure value is iterable
        elif isinstance(value, tuple):
            if not all(isinstance(v, basestring) for v in value):
                raise TypeError(
                    'host tuple contains non-string items')
            self.value = value
        else:
            raise TypeError('host must be string or tuple of strings')

        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        if 'restricted_hosts' not in conf:
            conf['restricted_hosts'] = set()
        conf['restricted_hosts'].update(self.value)

    def text(self):
        return u'host_restriction = {}'.format(self.value)

    phash = text

    def __call__(self, info_or_context, request):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        r_hosts = conf.get('restricted_hosts')

        # Abort if no restriction is configured or view is exempt
        if not r_hosts or not self.value:
            return True

        header = request.headers.get('host', 'www.zeit.de')

        if self.value is True:
            # View is available on all unclaimed hosts
            for host in r_hosts:
                if re.match('{}(\.staging)?\.zeit\.de'.format(host), header):
                    return False
            return True

        for host in self.value:
            if re.match('{}(\.staging)?\.zeit\.de'.format(host), header):
                return True

        return False


class VerticalPredicate(object):
    """Restricts requests to content that belongs to a specified vertical.

    See zeit.web.core.interfaces.IVertical for possible values. A value of '*'
    means allow all verticals.

    This is also the place to disable newly introduced verticals via feature
    toggles.

    Example usage:

        @zeit.web.view_config(
            context=zeit.content.article.interfaces.IArticle,
            vertical='zco')
        class ZCOArticleView(...):

    """

    def __init__(self, value, config):
        self.value = value

    def text(self):
        return u'vertical = {}'.format(self.value)

    phash = text

    def __call__(self, context, request):
        if self.value == '*':
            return True

        vertical = zeit.web.core.interfaces.IVertical(context)

        return vertical == self.value
