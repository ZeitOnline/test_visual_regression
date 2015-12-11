import pyramid.view
import zope.component

import zeit.content.author.interfaces
import zope.interface
import logging

from zeit.web.core.view import is_paginated
from zeit.web.site.view_centerpage import LegacyArea
from zeit.web.site.view_centerpage import LegacyModule
import zeit.web.core.interfaces

log = logging.getLogger(__name__)


@zeit.web.register_module('author_header')
class AuthorHeader(zeit.web.site.module.Module):

    def __init__(self, context):
        super(AuthorHeader, self).__init__(context)
        self.layout = 'author_header'

    @zeit.web.reify
    def author_img(self):
        return zeit.web.core.template.closest_substitute_image(
            self.context.image_group, 'zon-column')


@zeit.web.register_module('author_topics')
class AuthorTopics(zeit.web.site.module.Module):

    def __init__(self, context):
        super(AuthorTopics, self).__init__(context)
        self.layout = 'author_topics'


@zeit.web.register_module('author_bio')
class AuthorBio(zeit.web.site.module.Module):

    def __init__(self, context):
        super(AuthorBio, self).__init__(context)
        self.layout = 'author_bio'


@zeit.web.register_module('author_contact')
class AuthorContact(zeit.web.site.module.Module):

    def __init__(self, context):
        super(AuthorContact, self).__init__(context)
        self.layout = 'author_contact'


@pyramid.view.view_defaults(
    context=zeit.content.author.interfaces.IAuthor,
    renderer='templates/author.html')
@pyramid.view.view_config(name='')
class Author(zeit.web.core.view.Base):
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
        return self.context.display_name

    @zeit.web.reify
    def pagedescription(self):
        return self.context.display_name

    @zeit.web.reify
    def ranked_tags_list(self):
        return ''

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
    def author_img(self):
        return zeit.web.core.template.closest_substitute_image(
            self.context.image_group, 'zon-column')

    @zeit.web.reify
    def topic_links(self):
        return zeit.web.core.interfaces.ITopicLink(self.context)

    @zeit.web.reify
    def tab_areas(self):
        if is_paginated(self.context, self.request):
            return [self.area_articles]
        else:
            return [self.area_favourite_content, self.area_articles]

    @zeit.web.reify
    def area_favourite_content(self):
        return LegacyArea(
            [LegacyModule([c], layout='zon-small')
             for c in self.context.favourite_content],
            kind='author-favourite-content')

    @zeit.web.reify
    def area_articles(self):
        return create_author_article_area(self.context)

    @zeit.web.reify
    def has_author_comments(self):
        page_size = int(self.request.registry.settings.get(
            'author_comment_page_size', '10'))

        try:
            comments = zeit.web.core.comments.get_user_comments(
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
        page = int(self.request.GET.get('p', '1'))
        page_size = int(self.request.registry.settings.get(
            'author_comment_page_size', '10'))

        try:
            comments_meta = zeit.web.core.comments.get_user_comments(
                self.context, page=page, rows=page_size)
            comments = comments_meta['comments']
            return [UserCommentsArea(
                [LegacyModule([c], layout='user-comment') for c in comments],
                comments=comments_meta)]
        except zeit.web.core.comments.PagesExhaustedError:
            raise pyramid.httpexceptions.HTTPNotFound()
        except zeit.web.core.comments.UserCommentsException:
            return [UserCommentsArea([])]


def create_author_article_area(
        context, count=None, dedupe_favourite_content=True):
    cp = zeit.content.cp.centerpage.CenterPage()
    cp.uniqueId = context.uniqueId + u'/articles'
    area = cp.body.create_item('region').create_item('area')
    area.kind = 'author-articles'
    area.automatic_type = 'query'
    area.raw_query = u'author:"{}" AND (type:article)'.format(
        context.display_name)
    area.raw_order = 'date-first-released desc'
    if count is not None:
        area.count = count
    else:
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        area.count = int(conf.get('author_articles_page_size', '10'))
    area.automatic = True
    favourite_content = (
        context.favourite_content if dedupe_favourite_content else [])
    return AuthorArticleRanking(area, favourite_content)


class AuthorArticleRanking(zeit.web.site.area.ranking.Ranking):

    def __init__(self, context, favourite_content):
        super(AuthorArticleRanking, self).__init__(context)
        self.uids_above = [x.uniqueId for x in favourite_content]

    @zeit.web.reify
    def count(self):
        if self.page == 1:
            return self._count - len(self.uids_above)
        return self._count


class UserCommentsArea(LegacyArea):

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
