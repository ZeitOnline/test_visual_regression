# -*- coding: utf-8 -*-
import datetime
import logging

from pyramid.view import view_config
from pyramid.view import view_defaults
import babel.dates
import zope.component

import zeit.cms.workflow.interfaces
import zeit.connector.connector
import zeit.connector.interfaces
import zeit.content.article.edit.interfaces
import zeit.content.article.interfaces
import zeit.content.image.interfaces

import zeit.web
import zeit.web.core.article
import zeit.web.core.comments
import zeit.web.core.interfaces
import zeit.web.core.template
import zeit.web.core.utils
import zeit.web.core.view
import zeit.web.core.view_article
import zeit.web.site.view


log = logging.getLogger(__name__)


@view_defaults(context=zeit.content.article.interfaces.IArticle,
               custom_predicates=(zeit.web.site.view.is_zon_content,),
               request_method='GET')
@view_config(renderer='templates/article.html')
@view_config(custom_predicates=(zeit.web.site.view.is_zon_content,
             zeit.web.core.view.is_advertorial),
             renderer='templates/article_advertorial.html')
@view_config(name='komplettansicht',
             renderer='templates/komplett.html')
@view_config(custom_predicates=(zeit.web.site.view.is_zon_content,
             zeit.web.core.view.is_advertorial),
             name='komplettansicht',
             renderer='templates/article_advertorial_komplett.html')
class Article(zeit.web.core.view_article.Article, zeit.web.site.view.Base):

    @zeit.web.reify
    def canonical_url(self):
        """ Canonical for komplettansicht is first page """
        if not self.is_all_pages_view:
            return super(Article, self).canonical_url
        else:
            return self.resource_url

    @zeit.web.reify
    def meta_keywords(self):
        return [x for x in ([self.ressort.title(), self.supertitle] +
                super(Article, self).meta_keywords) if x]

    # Only needed to set tracking code on
    # http://www.zeit.de/newsletter/registriert?nl=premium.
    @zeit.web.reify
    def newsletter_optin_tracking(self):
        return self.request.GET.get('newsletter-optin', None)

    @zeit.web.reify
    def storystream(self):
        if self.context.storystreams:
            return self.context.storystreams[0].references
        else:
            return None

    @zeit.web.reify
    def storystream_items(self):
        storystream_cp = self.storystream
        if not storystream_cp:
            return ()
        atoms = list(zeit.content.cp.interfaces.ICMSContentIterable(
            storystream_cp))
        if self.context not in atoms:
            return atoms[:3]
        pos = atoms.index(self.context)
        if pos == 0:
            return atoms[:3]
        elif pos == len(atoms) - 1:
            return atoms[-3:]
        else:
            return atoms[pos - 1:pos + 2]

    @zeit.web.reify
    def has_series_attached(self):
        return getattr(self.context, 'serie', None)

    @zeit.web.reify
    def series(self):
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        uid = u'{}/{}'.format(
            conf.get('series_prefix', ''), self.context.serie.url)
        return zeit.cms.interfaces.ICMSContent(uid, None)


@view_config(name='seite',
             path_info='.*seite-(.*)',
             renderer='templates/article.html')
@view_config(name='seite',
             custom_predicates=(zeit.web.site.view.is_zon_content,
                                zeit.web.core.view.is_advertorial),
             path_info='.*seite-(.*)',
             renderer='templates/article_advertorial.html')
class ArticlePage(zeit.web.core.view_article.ArticlePage, Article):
    pass


@view_config(route_name='amp',
             renderer='templates/amp/article.html')
class AcceleratedMobilePageArticle(
        zeit.web.core.view_article.AcceleratedMobilePageArticle, Article):
    pass


def is_breaking_news(context, request):
    breaking = zeit.content.article.interfaces.IBreakingNews(context, None)
    if not (breaking and breaking.is_breaking):
        return False
    now = datetime.datetime.now(babel.dates.get_timezone('Europe/Berlin'))
    info = zeit.cms.workflow.interfaces.IPublishInfo(context, None)
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    seconds = zeit.web.core.utils.to_int(conf.get('breaking_news_timeout'))
    threshold = datetime.timedelta(seconds=seconds)
    return info and (now - info.date_first_released) < threshold


@view_config(custom_predicates=(zeit.web.site.view.is_zon_content,
                                is_breaking_news),
             renderer='templates/article_breaking.html')
class BreakingNews(Article):

    header_layout = 'breaking'


def is_column_article(context, request):
    return getattr(context, 'serie', None) and context.serie.column


def has_author_image(context, request):
    return zope.component.queryAdapter(
        context, zeit.web.core.interfaces.IImage, 'author')


@view_config(custom_predicates=(zeit.web.site.view.is_zon_content,
                                is_column_article,
                                has_author_image),
             renderer='templates/article.html')
@view_config(custom_predicates=(zeit.web.site.view.is_zon_content,
                                is_column_article,
                                has_author_image),
             name='komplettansicht',
             renderer='templates/komplett.html')
class ColumnArticle(Article):

    header_layout = 'column'


@view_config(name='seite',
             custom_predicates=(zeit.web.site.view.is_zon_content,
                                is_column_article,
                                has_author_image),
             path_info='.*seite-(.*)',
             renderer='templates/article.html')
class ColumnPage(zeit.web.core.view_article.ArticlePage, ColumnArticle):
    pass


@view_config(context=zeit.web.core.article.ILiveblogArticle,
             renderer='templates/liveblog.html')
class LiveblogArticle(Article):

    header_layout = 'liveblog'

    def __init__(self, context, request):
        super(LiveblogArticle, self).__init__(context, request)
        self.liveblog = zeit.web.core.interfaces.ILiveblogInfo(self.context)
