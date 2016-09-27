# coding: utf-8
import pyramid.view
import zope.component

import zeit.content.author.interfaces
import zope.interface
import logging

from zeit.web.core.view import is_paginated
import zeit.web.core.area.ranking
import zeit.web.core.centerpage
import zeit.web.core.interfaces

log = logging.getLogger(__name__)


@pyramid.view.view_defaults(
    context=zeit.content.author.interfaces.IAuthor,
    renderer='templates/author.html')
@pyramid.view.view_config(name='')
class Author(zeit.web.site.view.Base):
    """This view implements tabs that each have their own URL.
    To add a tab, subclass this, configure a different view name and provide
    a different ``tab_areas``.

    This class is also a view (without a view name, so serves as default) and
    displays the articles tab
    """

    advertising_enabled = True

    current_tab_name = ''

    @zeit.web.reify
    def pagetitle(self):
        return u'{} | Autoren{}'.format(
            self.context.display_name, self.pagetitle_suffix)

    @zeit.web.reify
    def social_pagetitle(self):
        return self.context.display_name

    @zeit.web.reify
    def pagedescription(self):
        return (
            u'Hier finden Sie Informationen sowie alle Texte und Artikel'
            u' von {} auf ZEIT ONLINE und aus DIE ZEIT im Überblick.'.format(
                self.context.display_name))

    @zeit.web.reify
    def meta_keywords(self):
        return []

    @zeit.web.reify
    def js_vars(self):
        return ''

    @zeit.web.reify
    def banner_channel(self):
        return ''

    @zeit.web.reify
    def ressort(self):
        return ''

    @zeit.web.reify
    def sub_ressort(self):
        return ''

    @zeit.web.reify
    def serie(self):
        return ''

    @zeit.web.reify
    def comment_counts(self):
        return {}

    @zeit.web.reify
    def tab_areas(self):
        if is_paginated(self.context, self.request) or (
                len(self.area_favourite_content) == 0):
            return [self.area_articles]
        else:
            return [self.area_favourite_content, self.area_articles]

    @zeit.web.reify
    def area_favourite_content(self):
        modules = []
        for index, content in enumerate(self.context.favourite_content):
            module = zeit.web.core.centerpage.TeaserModule(
                [content], layout='zon-small')
            module.force_mobile_image = not bool(index)
            modules.append(module)
        return zeit.web.core.centerpage.Area(
            modules, kind='author-favourite-content')

    @zeit.web.reify
    def area_articles(self):
        return create_author_article_area(self.context)

    @zeit.web.reify
    def has_author_comments(self):
        page_size = int(self.request.registry.settings.get(
            'author_comment_page_size', '10'))

        try:
            community = zope.component.getUtility(
                zeit.web.core.interfaces.ICommunity)
            comments = community.get_user_comments(
                self.context, page=1, rows=page_size)
            return comments and comments.get('page_total', 0) > 0
        except zeit.web.core.comments.UserCommentsException:
            log.warn('An exception occured, while trying to fetch comments.')

        return False


@pyramid.view.view_config(name='kommentare')
class Comments(Author):

    current_tab_name = 'kommentare'

    @zeit.web.reify
    def tab_areas(self):
        try:
            page = int(self.request.GET['p'])
        except (KeyError, ValueError):
            page = 1

        page_size = int(self.request.registry.settings.get(
            'author_comment_page_size', '10'))

        try:
            community = zope.component.getUtility(
                zeit.web.core.interfaces.ICommunity)
            comments_meta = community.get_user_comments(
                self.context, page=page, rows=page_size)
            if comments_meta is None:
                return [UserCommentsArea([])]
            comments = comments_meta['comments']
            return [UserCommentsArea([zeit.web.core.centerpage.TeaserModule(
                [c], layout='user-comment') for c in comments],
                comments=comments_meta)]
        except zeit.web.core.comments.PagesExhaustedError:
            raise pyramid.httpexceptions.HTTPNotFound()
        except zeit.web.core.comments.UserCommentsException:
            return [UserCommentsArea([])]


def create_author_article_area(
        context, count=None, dedupe_favourite_content=True):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    cp = zeit.content.cp.centerpage.CenterPage()
    zope.interface.alsoProvides(cp, zeit.cms.section.interfaces.IZONContent)
    cp.uniqueId = context.uniqueId + u'/articles'
    cp.body.clear()

    if dedupe_favourite_content:
        area = cp.body.create_item('region').create_item('area')
        for content in context.favourite_content:
            block = area.create_item('teaser')
            block.insert(0, content)

    area = area = cp.body.create_item('region').create_item('area')
    area.kind = 'author-articles'
    area.automatic_type = 'query'
    area.raw_query = unicode(
        conf.get('author_articles_query', 'author:"{}"')).format(
            context.display_name)
    area.raw_order = 'date-first-released desc'
    if count is not None:
        area.count = count
    else:
        area.count = int(conf.get('author_articles_page_size', '10'))
    area.automatic = True
    area.hide_dupes = True
    return AuthorRanking(area)


class AuthorRanking(zeit.web.core.area.ranking.Ranking):

    @zeit.web.reify
    def count(self):
        if self.page == 1:
            return self.context._count - self.surrounding_teasers
        return self.context._count

    @zeit.web.reify
    def start(self):
        return self.count * max(self.page - 1, 0)


class UserCommentsArea(zeit.web.core.centerpage.Area):

    zope.interface.implements(zeit.web.core.interfaces.IPagination)

    def __init__(self, arg, **kw):
        super(self.__class__, self).__init__(arg, **kw)
        self.kind = 'user-comments'
        self.comments = kw.get('comments', {'page_total': 0, 'page': 1})

    @zeit.web.reify
    def page(self):
        return self.comments['page']

    @zeit.web.reify
    def current_page(self):
        return self.page

    @zeit.web.reify
    def total_pages(self):
        return self.comments['page_total']

    @zeit.web.reify
    def pagination(self):
        pagination = zeit.web.core.template.calculate_pagination(
            self.current_page, self.total_pages)
        return pagination if pagination is not None else []

    @zeit.web.reify
    def pagination_info(self):
        return {
            'previous_label': u'Vorherige Seite',
            'previous_param': dict(p=self.current_page - 1),
            'next_label': u'Nächste Seite',
            'next_param': dict(p=self.current_page + 1)}

    def page_info(self, page_nr):
        return {
            'page_label': page_nr,
            'remove_get_param': 'p',
            'append_get_param': dict(p=page_nr)}
