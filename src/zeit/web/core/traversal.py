import urlparse
import logging

import pyramid.interfaces
import grokcore.component
import pyramid.traversal
import pyramid.httpexceptions
import zope.component
import zope.interface

import zeit.cms.repository.interfaces
import zeit.content.article.interfaces
import zeit.content.cp.interfaces
import zeit.content.dynamicfolder.interfaces
import zeit.content.gallery.interfaces
import zeit.content.video.interfaces
import zeit.magazin.interfaces

import zeit.web.site.module
import zeit.web.core.article
import zeit.web.core.centerpage
import zeit.web.core.template
import zeit.web.core.utils
import zeit.web.core.gallery
import zeit.web.core.interfaces


log = logging.getLogger(__name__)


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
        elif self.context.template == 'liveblog':
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
                form['q'] = u' '.join(tdict['request'].GET.getall('q'))
                form['type'] = u' '.join(tdict['request'].GET.getall('type'))
                form['mode'] = tdict['request'].GET.get('mode')
                form['sort'] = tdict['request'].GET.get('sort')
                area.raw_query = form.raw_query
                area.sort_order = form.sort_order
                area.query = form.query
            else:
                form = zeit.web.site.module.search_form.Form(tdict['context'])

            form['page'] = tdict['request'].GET.get('p')

            # Validate page number
            try:
                page_num = int(form['page'])
            except ValueError:
                # page_num is not a number
                raise pyramid.httpexceptions.HTTPNotFound()
            except TypeError:
                # page_num is None
                pass
            else:
                if page_num > area.total_pages or page_num <= 0:
                    raise pyramid.httpexceptions.HTTPNotFound()
            area.page = form.page
        # XXX block-sensitive shenanigans continue
        region = zeit.web.core.utils.find_block(
            self.context, attrib='area', kind='gallery')
        # XXX Galleries are included via both a region and an area with
        # kind=gallery; find_block() unfortunately does not allow us to
        # express this in a query...
        if region:
            area = zeit.web.core.utils.find_block(
                region, attrib='area', kind='gallery')
            if area:
                area = zeit.web.core.centerpage.get_area(area)
                area.page = tdict['request'].GET.get('p')


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


@traverser(zeit.content.dynamicfolder.interfaces.IRepositoryDynamicFolder)
class DynamicFolder(CenterPage):

    def __call__(self, tdict):
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
        # XXX: Let's hope no video is ever called 'imagegroup'
        #      or 'comment-form' or 'report-form'. (ND)
        if tdict['view_name'] not in (
                'imagegroup', 'comment-form', 'report-form'):
            tdict['request'].headers['X-SEO-Slug'] = tdict['view_name']
            tdict['view_name'] = ''
