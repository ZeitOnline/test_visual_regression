# -*- coding: utf-8 -*-
import logging

import pyramid.view

import zeit.content.article.edit.interfaces
import zeit.content.article.interfaces

import zeit.web
import zeit.web.core.article
import zeit.web.core.comments
import zeit.web.core.interfaces
import zeit.web.core.template
import zeit.web.core.view
import zeit.web.core.view_article
import zeit.web.core.view_comment

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
    def comments(self):
        if not self.show_commentthread:
            return
        thread = zeit.web.core.comments.get_thread(
            self.context.uniqueId, sort='desc')
        if thread and thread.get('request_failed'):
            return None
        return thread

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

    is_longform = True
    pagetitle_suffix = u' | ZEIT ONLINE'

    @zeit.web.reify
    def header_img(self):
        obj = self.first_body_obj
        if zeit.content.article.edit.interfaces.IImage.providedBy(obj):
            return self._create_obj(zeit.web.core.block.HeaderImage, obj)

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


@pyramid.view.view_config(context=zeit.web.core.article.IFeatureLongform,
                          renderer='templates/feature_longform.html')
class FeatureLongform(LongformArticle):
    pass


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

    def __init__(self, *args, **kwargs):
        super(PhotoclusterArticle, self).__init__(*args, **kwargs)
        for page in self.pages:
            for index in range(len(page)):
                if issubclass(
                        type(page[index]), zeit.web.core.gallery.Gallery):
                    cls = type('Photocluster',
                               (zeit.web.core.gallery.Gallery,), {})
                    page[index] = cls(page[index].context)


@pyramid.view.view_config(route_name='amp',
                          renderer='templates/amp/article.html')
class AcceleratedMobilePageArticle(Article):
    pass


@pyramid.view.view_config(name='teaser',
                          renderer='templates/teaser.html')
class Teaser(Article):

    @zeit.web.reify
    def teaser_text(self):
        return self.context.teaser
