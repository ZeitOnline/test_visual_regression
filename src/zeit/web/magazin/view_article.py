# -*- coding: utf-8 -*-
import zeit.content.article.interfaces

import zeit.web
import zeit.web.core.article
import zeit.web.core.view
import zeit.web.core.view_article
import zeit.web.magazin.article
import zeit.web.magazin.view


@zeit.web.view_defaults(
    context=zeit.content.article.interfaces.IArticle,
    vertical='zmo')
@zeit.web.view_config(
    custom_predicates=(zeit.web.core.view.is_advertorial,),
    renderer='templates/advertorial.html')
@zeit.web.view_config(
    renderer='templates/article.html')
@zeit.web.view_config(
    custom_predicates=(zeit.web.core.view.is_paywalled,),
    renderer='zeit.web.core:templates/paywall.html')
@zeit.web.view_config(
    name='komplettansicht',
    renderer='templates/komplettansicht.html')
@zeit.web.view_config(
    custom_predicates=(zeit.web.core.view.is_paywalled,),
    name='komplettansicht',
    renderer='zeit.web.core:templates/paywall.html')
@zeit.web.view_config(
    context=zeit.web.magazin.article.IColumnArticle,
    custom_predicates=(zeit.web.core.view.is_paywalled,),
    renderer='zeit.web.core:templates/paywall.html')
@zeit.web.view_config(
    context=zeit.web.magazin.article.IShortformArticle,
    custom_predicates=(zeit.web.core.view.is_paywalled,),
    renderer='zeit.web.core:templates/paywall.html')
@zeit.web.view_config(
    context=zeit.web.magazin.article.IPhotoclusterArticle,
    custom_predicates=(zeit.web.core.view.is_paywalled,),
    renderer='zeit.web.core:templates/paywall.html')
class Article(zeit.web.core.view_article.Article,
              zeit.web.magazin.view.Content):
    pass


@zeit.web.view_defaults(vertical='zmo')
@zeit.web.view_config(
    name='seite',
    path_info='.*seite-(.*)',
    renderer='templates/article.html')
@zeit.web.view_config(
    name='seite',
    custom_predicates=(zeit.web.core.view.is_advertorial,),
    path_info='.*seite-(.*)',
    renderer='templates/advertorial.html')
@zeit.web.view_config(
    name='seite',
    custom_predicates=(zeit.web.core.view.is_paywalled,),
    path_info='.*seite-(.*)',
    renderer='zeit.web.core:templates/paywall.html')
class ArticlePage(zeit.web.core.view_article.ArticlePage, Article):
    pass


@zeit.web.view_defaults(
    context=zeit.web.magazin.article.ILongformArticle,
    vertical='zmo')
@zeit.web.view_config(
    renderer='templates/longform.html')
@zeit.web.view_config(
    custom_predicates=(zeit.web.core.view.is_paywalled,),
    renderer='zeit.web.core:templates/paywall.html')
class LongformArticle(Article):

    pagetitle_suffix = u' | ZEIT ONLINE'

    def __init__(self, context, request):
        super(LongformArticle, self).__init__(context, request)
        self.view_name = 'longform'

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


@zeit.web.view_defaults(
    context=zeit.web.magazin.article.ILongformArticle,
    vertical='zon')
@zeit.web.view_config(
    renderer='templates/feature_longform.html')
@zeit.web.view_config(
    custom_predicates=(zeit.web.core.view.is_paywalled,),
    renderer='zeit.web.core:templates/paywall.html')
class FeatureLongform(LongformArticle):

    def __init__(self, context, request):
        super(LongformArticle, self).__init__(context, request)
        self.view_name = 'feature_longform'

    @zeit.web.reify
    def adwords(self):
        keywords = super(FeatureLongform, self).adwords
        keywords.remove('zeitmz')
        return keywords

    @zeit.web.reify
    def publisher_name(self):
        return 'ZEIT ONLINE'

    @zeit.web.reify
    def site_name(self):
        return self.publisher_name

    @zeit.web.reify
    def twitter_username(self):
        return 'zeitonline'


@zeit.web.view_config(
    context=zeit.web.magazin.article.IShortformArticle,
    renderer='templates/shortform.html')
class ShortformArticle(Article):
    pass


@zeit.web.view_config(
    context=zeit.web.magazin.article.IColumnArticle,
    renderer='templates/column.html')
class ColumnArticle(Article):
    pass


@zeit.web.view_config(
    context=zeit.web.magazin.article.IPhotoclusterArticle,
    renderer='templates/photocluster.html')
class PhotoclusterArticle(Article):

    def __init__(self, context, request):
        super(PhotoclusterArticle, self).__init__(context, request)
        for page in self.pages:
            for block in page:
                if isinstance(block, zeit.web.core.block.Gallery):
                    block.block_type = 'photocluster'


@zeit.web.view_config(
    route_name='amp',
    renderer='templates/amp/article.html')
class AcceleratedMobilePageArticle(
        zeit.web.core.view_article.AcceleratedMobilePageArticle, Article):
    pass


@zeit.web.view_config(
    name='teaser',
    renderer='templates/teaser.html')
class Teaser(Article):

    @zeit.web.reify
    def teaser_text(self):
        return self.context.teaser
