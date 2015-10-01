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
             renderer='templates/article_komplett.html')
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
    def pagetitle(self):
        try:
            title = zeit.seo.interfaces.ISEO(self.context).html_title
            assert title
        except (AssertionError, TypeError):
            if self.page_nr > 1 and self.current_page.teaser:
                title = ': '.join(
                    [t for t in (
                        self.supertitle, self.current_page.teaser) if t])
            else:
                title = ': '.join(
                    [t for t in (
                        self.supertitle, self.title) if t])
        if title:
            return title + (u'' if self.is_hp else self.pagetitle_suffix)
        return self.seo_title_default

    @zeit.web.reify
    def pdf_link(self):
        server = 'http://pdf.zeit.de/'
        path = '/'.join(self.request.traversed)
        return server + path + '.pdf'

    @zeit.web.reify
    def print_link(self):
        url = self.content_url
        prefix = '/komplettansicht'

        try:
            if len(self.pages) == 1:
                prefix = ''
        except:
            pass

        path = prefix + '?print=true'
        return url + path

    @zeit.web.reify
    def breadcrumbs(self):
        breadcrumbs = super(Article, self).breadcrumbs
        # News
        if self.ressort == 'news':
            breadcrumbs.extend([('News', 'http://xml.zeit.de/news/index')])
            self.breadcrumbs_by_title(breadcrumbs)
            return breadcrumbs
        # Archive article
        if self.product_id in ('ZEI', 'ZEAR'):
            # Beware, we have some pretty messy archive data...
            try:
                breadcrumbs.extend([
                    ('DIE ZEIT Archiv', 'http://xml.zeit.de/archiv'),
                    ("Jahrgang {}".format(self.context.year),
                        'http://xml.zeit.de/{}/index'.format(
                            self.context.year)),
                    ("Ausgabe: {0:02d}".format(self.context.volume),
                        'http://xml.zeit.de/{0}/{1:02d}/index'.format(
                            self.context.year, self.context.volume))])
                self.breadcrumbs_by_title(breadcrumbs)
                return breadcrumbs
            except ValueError:
                return self.breadcrumbs_by_title(breadcrumbs)
        # Ordinary articles
        self.breadcrumbs_by_navigation(breadcrumbs)
        page_teaser = self.current_page.teaser
        if len(page_teaser) > 0:
            breadcrumbs.extend([(page_teaser, self.context.uniqueId)])
        else:
            self.breadcrumbs_by_title(breadcrumbs)
        return breadcrumbs

    @zeit.web.reify
    def has_cardstack(self):
        return len(self.context.xml.xpath('/article/body//cardstack')) > 0

    @zeit.web.reify
    def advertorial_marker(self):
        try:
            return (
                self.context.advertisement_title,
                self.context.advertisement_text,
                self.cap_title)
        except AttributeError:
            return None


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
    pass


def is_column_article(context, request):
    return getattr(context, 'serie', None) and context.serie.column


def has_author_image(context, request):
    authors = zeit.web.core.article.convert_authors(context)
    if not authors:
        return False
    return zeit.web.core.template.closest_substitute_image(
        authors[0]['image_group'], 'zon-column')


@view_config(custom_predicates=(zeit.web.site.view.is_zon_content,
                                is_column_article,
                                has_author_image),
             renderer='templates/column.html')
@view_config(custom_predicates=(zeit.web.site.view.is_zon_content,
                                is_column_article,
                                has_author_image),
             name='komplettansicht',
             renderer='templates/column_komplett.html')
class ColumnArticle(Article):

    @zeit.web.reify
    def author_img(self):
        if not self.authors:
            return
        return zeit.web.core.template.closest_substitute_image(
            self.authors[0]['image_group'], 'zon-column')


@view_config(name='seite',
             custom_predicates=(zeit.web.site.view.is_zon_content,
                                is_column_article,
                                has_author_image),
             path_info='.*seite-(.*)',
             renderer='templates/column.html')
class ColumnPage(zeit.web.core.view_article.ArticlePage, ColumnArticle):
    pass


@view_config(context=zeit.web.core.article.ILiveblogArticle,
             renderer='templates/liveblog.html')
class LiveblogArticle(Article):

    def __init__(self, *args, **kwargs):
        super(LiveblogArticle, self).__init__(*args, **kwargs)
        self.liveblog_last_modified = self.date_last_modified
        self.liveblog_is_live = False
        for page in self.pages:
            for block in page.blocks:
                if isinstance(block, zeit.web.core.block.Liveblog):
                    self.liveblog_is_live = block.is_live
                    if block.last_modified:
                        self.liveblog_last_modified = block.last_modified
                    # break the inner loop
                    break
            else:
                # continue if the inner loop wasn't broken
                continue
            # inner loop was broken, break the outer
            break
