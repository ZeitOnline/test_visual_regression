# -*- coding: utf-8 -*-
from babel.dates import get_timezone
from pyramid.renderers import render_to_response
from pyramid.view import view_config
from zeit.cms.workflow.interfaces import IPublishInfo, IModified
from zeit.content.image.interfaces import IImageMetadata
from zeit.magazin.interfaces import IArticleTemplateSettings, INextRead
import zeit.content.article.interfaces
from .comments import get_thread


class Base(object):
    """Base class for all views."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return {}


_navigation = {'start': ('Start', 'http://www.zeit.de/index', 'myid1'),
               'zmo':('ZEIT Magazin', 'http://www.zeit.de/index', 'myid_zmo'),
               'lebensart': (
                   'ZEIT Magazin',
                   'http://www.zeit.de/magazin/index',
                   'myid2',
               ),
               'mode': (
                   'Mode',
                   'http://www.zeit.de/magazin/lebensart/index',
                   'myid3',
               ), }


@view_config(route_name='json',
             context=zeit.content.article.interfaces.IArticle,
             renderer='json')
@view_config(context=zeit.content.article.interfaces.IArticle,
             renderer='templates/article.html')
class Article(Base):

    def __call__(self):
        self.context.advertising_enabled = True
        self.context.main_nav_full_width = False
        self.context.is_longform = False
        self.comments = self._comments()

        if IArticleTemplateSettings(self.context).template == 'longform':
            self.context.advertising_enabled = False
            self.context.main_nav_full_width = True
            self.context.is_longform = True
            return render_to_response('templates/longform.html',
                                      {"view": self},
                                      request=self.request)
        return {}

    @property
    def title(self):
        return self.context.title

    @property
    def subtitle(self):
        return self.context.subtitle

    @property
    def supertitle(self):
        return self.context.supertitle

    @property
    def pages(self):
        return zeit.frontend.interfaces.IPages(self.context)

    @property
    def header_img(self):
        return self.context.header_img

    @property
    def author(self):
        try:
            author = self.context.authors[0]
        except IndexError:
            author = None
        return {
            'name': author.display_name if author else None,
            'href': author.uniqueId if author else None,
            'prefix': " von " if self.context.genre else "Von ",
            'suffix': ', ' if self.location else None,
        }

    @property
    def publish_date(self):
        tz = get_timezone('Europe/Berlin')
        date = IPublishInfo(
            self.context).date_last_published_semantic
        if date:
            return date.astimezone(tz)

    @property
    def publish_date_meta(self):
        return IPublishInfo(
            self.context).date_last_published_semantic.isoformat()

    @property
    def last_modified_date(self):
        return IModified(self.context).date_last_modified

    @property
    def rankedTags(self):
        return self.context.keywords

    @property
    def genre(self):
        return self.context.genre

    @property
    def source(self):
        return self.context.copyrights or self.context.product_text

    @property
    def location(self):
        return None  # XXX not implemented in zeit.content.article yet

    @property
    def focussed_nextread(self):
        nextread = INextRead(self.context)
        related = nextread.nextread
        if related:
            image = related.main_image
            if image is not None:
                image = {
                    'uniqueId': image.uniqueId,
                    'caption': (related.main_image_block.custom_caption
                                or IImageMetadata(image).caption),
                }
            else:
                image = {'uniqueId': None}
            return {'layout': nextread.nextread_layout,
                    'article': related,
                    'image': image}

    @property
    def breadcrumb(self):
        l = [_navigation['start']]
        l.append(_navigation['zmo'])
        if self.context.ressort in _navigation:
            l.append(_navigation[self.context.ressort])
        if self.context.sub_ressort in _navigation:
            l.append(_navigation[self.context.sub_ressort])
        if self.title:
            l.append((self.title, 'http://localhost'))
        return l


    def _comments(self):
        return get_thread(unique_id=self.context.uniqueId, request=self.request)


class Gallery(Base):
    pass


@view_config(route_name='json',
             context=zeit.content.article.interfaces.IArticle,
             renderer='json', name='teaser')
@view_config(name='teaser',
             context=zeit.content.article.interfaces.IArticle,
             renderer='templates/teaser.html')
class Teaser(Article):

    @property
    def teaser_text(self):
        """docstring for teaser"""
        return self.context.teaser
