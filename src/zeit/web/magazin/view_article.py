import logging

from pyramid.view import view_config
from pyramid.decorator import reify

import zeit.connector.connector
import zeit.connector.interfaces
import zeit.content.article.edit.interfaces
import zeit.content.article.interfaces
import zeit.content.image.interfaces

import zeit.web
import zeit.web.core.article
import zeit.web.core.comments
import zeit.web.core.interfaces
import zeit.web.core.reach
import zeit.web.core.template
import zeit.web.core.view
import zeit.web.core.view_article

import zeit.web.magazin.view


log = logging.getLogger(__name__)


@view_config(context=zeit.content.article.interfaces.IArticle,
             custom_predicates=(zeit.web.magazin.view.is_zmo_content,
                                zeit.web.magazin.view.is_advertorial),
             renderer='templates/advertorial.html')
@view_config(context=zeit.content.article.interfaces.IArticle,
             custom_predicates=(zeit.web.magazin.view.is_zmo_content,),
             renderer='templates/article.html')
@view_config(context=zeit.content.article.interfaces.IArticle,
             custom_predicates=(zeit.web.magazin.view.is_zmo_content,),
             name='komplettansicht',
             renderer='templates/article_komplett.html')
class Article(zeit.web.core.view_article.Article, zeit.web.magazin.view.Base):
    @zeit.web.reify
    def issue_format(self):
        return u' Nr. %d/%d'


@view_config(context=zeit.content.article.interfaces.IArticle,
             custom_predicates=(zeit.web.magazin.view.is_zmo_content,),
             name='seite',
             path_info='.*seite-(.*)',
             renderer='templates/article.html')
class ArticlePage(zeit.web.core.view_article.ArticlePage, Article):
    pass


@view_config(context=zeit.web.core.article.ILongformArticle,
             custom_predicates=(zeit.web.magazin.view.is_zmo_content,),
             renderer='templates/longform.html')
class LongformArticle(Article):

    main_nav_full_width = True
    is_longform = True

    @zeit.web.reify
    def header_img(self):
        obj = self.first_body_obj
        if zeit.content.article.edit.interfaces.IImage.providedBy(obj):
            img = self._create_obj(zeit.web.core.block.HeaderImage, obj)
            if img:
                self._copyrights.setdefault(img.uniqueId, img)
            return img

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


@view_config(context=zeit.web.core.article.IFeatureLongform,
             custom_predicates=(zeit.web.magazin.view.is_zmo_content,),
             renderer='templates/feature_longform.html')
class FeatureLongform(LongformArticle):
    @reify
    def breadcrumb(self):
        crumb = self._navigation
        l = [crumb['start']]
        if self.context.ressort in crumb:
            l.append(crumb[self.context.ressort])
        if self.context.sub_ressort in crumb:
            l.append(crumb[self.context.sub_ressort])
        if self.title:
            l.append((self.title, ''))
        return l


@view_config(context=zeit.web.core.article.IShortformArticle,
             custom_predicates=(zeit.web.magazin.view.is_zmo_content,),
             renderer='templates/shortform.html')
class ShortformArticle(Article, zeit.web.core.view_article.Article):
    pass


@view_config(context=zeit.web.core.article.IColumnArticle,
             custom_predicates=(zeit.web.magazin.view.is_zmo_content,),
             renderer='templates/column.html')
class ColumnArticle(Article, zeit.web.core.view_article.Article):
    pass


@view_config(context=zeit.web.core.article.IPhotoclusterArticle,
             custom_predicates=(zeit.web.magazin.view.is_zmo_content,),
             renderer='templates/photocluster.html')
class PhotoclusterArticle(Article, zeit.web.core.view_article.Article):

    def __init__(self, *args, **kwargs):
        super(PhotoclusterArticle, self).__init__(*args, **kwargs)
        for page in self.pages:
            for index in range(len(page)):
                if issubclass(
                        type(page[index]), zeit.web.core.gallery.Gallery):
                    cls = type('Photocluster',
                               (zeit.web.core.gallery.Gallery,), {})
                    page[index] = cls(page[index].context)


@view_config(name='teaser',
             context=zeit.content.article.interfaces.IArticle,
             custom_predicates=(zeit.web.magazin.view.is_zmo_content,),
             renderer='templates/teaser.html')
class Teaser(Article, zeit.web.core.view_article.Article):

    @zeit.web.reify
    def teaser_text(self):
        return self.context.teaser
