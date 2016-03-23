import urlparse
import logging

import grokcore.component
import pyramid.httpexceptions
import pyramid.interfaces
import pyramid.traversal
import pyramid.urldispatch
import zc.sourcefactory.source
import zope.component
import zope.interface

import zeit.cms.repository.interfaces
import zeit.content.article.interfaces
import zeit.content.cp.interfaces
import zeit.content.dynamicfolder.interfaces
import zeit.content.gallery.interfaces
import zeit.content.video.interfaces

import zeit.web.core.article
import zeit.web.core.centerpage
import zeit.web.core.gallery
import zeit.web.core.interfaces
import zeit.web.core.template
import zeit.web.core.utils


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


@traverser(zeit.content.article.interfaces.IArticle)
class Article(Traversable):

    def __call__(self, tdict):
        if urlparse.urlparse(
                self.context.uniqueId).path.startswith('/feature/'):
            # ToDo: Remove when Longform will be generally used on
            # www.zeit.de. By then do not forget to remove marker
            # interfaces from uniqueID http://xml.zeit.de/feature (RD)
            zope.interface.alsoProvides(
                self.context, zeit.web.core.article.IFeatureLongform)
        elif self.context.template == 'longform':
            zope.interface.alsoProvides(
                self.context, zeit.web.core.article.ILongformArticle)
        elif self.context.template == 'short':
            zope.interface.alsoProvides(
                self.context, zeit.web.core.article.IShortformArticle)
        elif self.context.template == 'column':
            zope.interface.alsoProvides(
                self.context, zeit.web.core.article.IColumnArticle)
        elif zeit.web.core.template.is_liveblog(self.context):
            zope.interface.alsoProvides(
                self.context, zeit.web.core.article.ILiveblogArticle)
        elif self.context.template == 'photocluster':
            zope.interface.alsoProvides(
                self.context, zeit.web.core.article.IPhotoclusterArticle)

        if tdict['view_name'].startswith('seite') and not tdict['subpath']:
            tdict['view_name'] = 'seite'


@traverser(zeit.content.gallery.interfaces.IGallery)
class Gallery(Traversable):

    def __call__(self, tdict):
        metadata = zeit.content.gallery.interfaces.IGalleryMetadata(
            self.context)

        if metadata.type == 'zmo-product':
            zope.interface.alsoProvides(
                self.context, zeit.web.core.gallery.IProductGallery)
        else:
            zope.interface.alsoProvides(
                self.context, zeit.web.core.gallery.IGallery)


@traverser(zeit.content.cp.interfaces.ICenterPage)
class CenterPage(Traversable):

    def __call__(self, tdict):
        # XXX: RAM block sensitive traversal hacking is pretty inelegant,
        #      let's think of something better. (ND)
        area = zeit.web.core.utils.find_block(
            self.context, attrib='area', kind='ranking')
        if area:
            area = zeit.web.core.centerpage.get_area(area)
            form = zeit.web.core.utils.find_block(
                self.context, module='search-form')
            if form:
                form = zeit.web.core.template.get_module(form)
                area.raw_query = form.raw_query
                area.raw_order = form.raw_order
                area.sort_order = form.sort_order


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


@traverser(zeit.cms.repository.interfaces.IFolder)
class Folder(Traversable):

    def __call__(self, tdict):
        """Redirect traversed folders and the repository root to a location
        suffixed by `/index`.
        """

        if tdict['view_name']:
            # We're not at the end of the URL yet.
            return
        if getattr(tdict['request'].matched_route, 'name', '') == 'home' or (
                type(tdict['context']) == zeit.cms.repository.folder.Folder):
            url = zeit.web.core.utils.update_path(
                tdict['request'].url, tdict['request'].path, 'index')
            raise pyramid.httpexceptions.HTTPMovedPermanently(location=url)


@traverser(zeit.content.dynamicfolder.interfaces.IRepositoryDynamicFolder)
class DynamicFolder(CenterPage):

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


class BlacklistSource(zeit.cms.content.sources.SimpleContextualXMLSource):
    # Only contextual so we can customize source_class

    product_configuration = 'zeit.web'
    config_url = 'blacklist-url'

    class source_class(zc.sourcefactory.source.FactoredContextualSource):

        def matches(self, path):
            return self.factory.matches(path)

    def matches(self, path):
        for matcher in self.compile():
            if matcher(path) is not None:
                return True
        return False

    @CONFIG_CACHE.cache_on_arguments()
    def compile(self):
        matchers = []
        for pattern in self.getValues(None):
            matcher, _ = pyramid.urldispatch._compile_route(pattern)
            matchers.append(matcher)
        return matchers

BLACKLIST = BlacklistSource()(None)


@zope.interface.implementer(pyramid.interfaces.IRoutesMapper)
class RoutesMapper(pyramid.urldispatch.RoutesMapper):

    def __call__(self, request):
        # Duplicated from super class (sigh).
        try:
            path = pyramid.urldispatch.decode_path_info(
                request.environ['PATH_INFO'] or '/')
        except KeyError:
            path = '/'
        except UnicodeDecodeError as e:
            raise pyramid.exceptions.URLDecodeError(
                e.encoding, e.object, e.start, e.end, e.reason)

        # It would be nice if we could use a custom `Route` class (to perform
        # the blacklist matching in the Route.match() method) -- then we
        # wouldn't need to touch RoutesMapper at all. However, Pyramid's
        # configurator doesn't allow that easily.
        if not request.headers.get('Host', '').startswith('newsfeed') and (
                BLACKLIST.matches(path)):
            return {'route': self.routes['blacklist'], 'match': {}}

        return super(RoutesMapper, self).__call__(request)
