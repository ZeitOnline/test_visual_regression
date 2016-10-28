# -*- coding: utf-8 -*-
import logging

import pyramid.view

import zeit.content.article.edit.interfaces
import zeit.content.article.interfaces

import zeit.web
import zeit.web.core.article
import zeit.web.core.comments
import zeit.web.core.interfaces
import zeit.web.core.view
import zeit.web.core.view_article

import zeit.web.magazin.view


log = logging.getLogger(__name__)


@pyramid.view.view_defaults(
    context=zeit.content.article.interfaces.IArticle,
    custom_predicates=(zeit.web.magazin.view.is_zmo_content,),
    request_method='GET')
@pyramid.view.view_config(
    custom_predicates=(zeit.web.magazin.view.is_zmo_content,
                       zeit.web.core.view.is_advertorial),
    renderer='templates/advertorial.html')
@pyramid.view.view_config(renderer='templates/article.html')
@pyramid.view.view_config(name='komplettansicht',
                          renderer='templates/article_komplett.html')
class Article(zeit.web.core.view_article.Article, zeit.web.magazin.view.Base):

    @zeit.web.reify
    def genre(self):
        prefix = 'ein'
        if self.context.genre in (
                'analyse', 'glosse', 'nachricht', 'reportage'):
            prefix = 'eine'
        if self.context.genre:
            return prefix + ' ' + self.context.genre.title()


@pyramid.view.view_config(name='seite',
                          path_info='.*seite-(.*)',
                          renderer='templates/article.html')
class ArticlePage(zeit.web.core.view_article.ArticlePage, Article):
    pass


@pyramid.view.view_config(context=zeit.web.core.article.ILongformArticle,
                          renderer='templates/longform.html')
class LongformArticle(Article):

    pagetitle_suffix = u' | ZEIT ONLINE'

    @zeit.web.reify
    def adwords(self):
        keywords = super(LongformArticle, self).adwords
        keywords.extend(['longform', 'noiqdband'])
        return keywords

    @zeit.web.reify
    def is_top_of_mind(self):
        return False

    @zeit.web.reify
    def banner_type(self):
        return 'longform'

    @zeit.web.reify
    def show_date_format(self):
        return 'short'

    @zeit.web.reify
    def share_buttons(self):
        return 'big'


@pyramid.view.view_config(context=zeit.web.core.article.IFeatureLongform,
                          renderer='templates/feature_longform.html')
class FeatureLongform(LongformArticle):

    @zeit.web.reify
    def adwords(self):
        keywords = super(FeatureLongform, self).adwords
        keywords.remove('zeitmz')
        return keywords

    @zeit.web.reify
    def publisher_name(self):
        return 'ZEIT ONLINE'

    @zeit.web.reify
    def twitter_username(self):
        return 'zeitonline'


@pyramid.view.view_config(context=zeit.web.core.article.IShortformArticle,
                          renderer='templates/shortform.html')
class ShortformArticle(Article):
    pass


@pyramid.view.view_config(context=zeit.web.core.article.IColumnArticle,
                          renderer='templates/column.html')
class ColumnArticle(Article):
    pass


@pyramid.view.view_config(context=zeit.web.core.article.IPhotoclusterArticle,
                          renderer='templates/photocluster.html')
class PhotoclusterArticle(Article):

    def __init__(self, context, request):
        super(PhotoclusterArticle, self).__init__(context, request)
        for page in self.pages:
            for block in page:
                if isinstance(block, zeit.web.core.block.Gallery):
                    block.block_type = 'photocluster'


@pyramid.view.view_config(route_name='amp',
                          renderer='templates/amp/article.html')
class AcceleratedMobilePageArticle(
        zeit.web.core.view_article.AcceleratedMobilePageArticle, Article):
    pass


@pyramid.view.view_config(name='teaser',
                          renderer='templates/teaser.html')
class Teaser(Article):

    @zeit.web.reify
    def teaser_text(self):
        return self.context.teaser
