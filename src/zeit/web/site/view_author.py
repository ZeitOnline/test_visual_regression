# coding: utf-8
import logging
import math

import lxml.objectify
import pyramid.httpexceptions
import zope.component
import zope.interface

import zeit.content.author.interfaces
import zeit.content.cp.blocks.mail

from zeit.web.core.view import is_paginated
import zeit.web
import zeit.web.core.area.ranking
import zeit.web.core.centerpage
import zeit.web.core.interfaces

log = logging.getLogger(__name__)


@zeit.web.view_defaults(
    context=zeit.content.author.interfaces.IAuthor,
    renderer='templates/author.html')
@zeit.web.view_config(name='')
class Author(zeit.web.core.view_centerpage.AreaProvidingPaginationMixin,
             zeit.web.site.view.Base):
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
        return 'administratives/autoren'

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
    def area_providing_pagination(self):
        for area in self.tab_areas:
            if zeit.web.core.interfaces.IPagination.providedBy(area):
                return area

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

    @zeit.web.reify
    def author_email(self):
        return self.context.email

@zeit.web.view_config(name='feedback')
class Feedback(Author):

    current_tab_name = 'feedback'

    @zeit.web.reify
    def tab_areas(self):
        return [self.area_feedback]

    @zeit.web.reify
    def area_feedback(self):
        if not self.context.email:
            return None
        area = zeit.web.core.centerpage.Area([], kind='author-feedback')
        module = zeit.content.cp.blocks.mail.MailBlock(
            area, lxml.objectify.XML('<dummy/>'))

        module.to = 'hennes.roemmer@zeit.de' # self.context.email
        module.subject = 'Sie haben Feedback erhalten'
        module.author_name = self.context.display_name
        module.success_message = 'Ihr Feedback wurde erfolgreich verschickt.'

        area.append(zeit.web.core.centerpage.get_module(module))
        return area

@zeit.web.view_config(name='kommentare')
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
            block.insert(0, content, suppress_errors=True)

    area = cp.body.create_item('region').create_item('area')
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
        if self.page == 1:
            return 0
        return self.count * (self.page - 1) - self.surrounding_teasers

    @zeit.web.reify
    def total_pages(self):
        count = self.context._count
        items = self.hits + self.surrounding_teasers
        if items > 0 < count:
            return int(math.ceil(float(items) / float(count)))
        return 0


class UserCommentsArea(zeit.web.core.centerpage.Area):

    zope.interface.implements(zeit.web.core.interfaces.IPagination)

    def __init__(self, arg, **kw):
        super(self.__class__, self).__init__(arg, **kw)
        self.kind = 'user-comments'
        self.comments = kw.get('comments', {'page_total': 0, 'page': 1})
        self.request = pyramid.threadlocal.get_current_request()

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
            'next_label': u'Nächste Seite'}

    def page_info(self, page_nr):
        url = zeit.web.core.utils.remove_get_params(self.request.url, 'p')
        if page_nr > 1:
            url = zeit.web.core.utils.add_get_params(url, **dict(p=page_nr))

        return {
            'label': page_nr,
            'url': url
        }
