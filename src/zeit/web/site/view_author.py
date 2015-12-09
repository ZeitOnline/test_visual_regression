import pyramid.view
import zope.component

import zeit.content.author.interfaces

from zeit.web.core.view import is_paginated
from zeit.web.site.view_centerpage import LegacyArea
from zeit.web.site.view_centerpage import LegacyModule
from zeit.web.site.view_centerpage import LegacyRegion
import zeit.web.core.interfaces


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


@pyramid.view.view_config(
    renderer='templates/author.html',
    context=zeit.content.author.interfaces.IAuthor)
class Author(zeit.web.core.view.Base):
    """This view implements tabs that each have their own URL.
    To add a tab, subclass this, configure a different view name and provide
    an ``area_for_tab``.

    This class is also a view (without a view name, so serves as default) and
    displays the articles tab

    We use a region kind='tabbed' to render the tab list menu, described in
    ``tabs`` and ``current_tab``; this region also contains the
    ``area_for_tab``.

    """

    advertising_enabled = True

    tabs = [
        {'name': '', 'title': 'Artikel'},
        {'name': 'kommentare', 'title': 'Kommentare'},
    ]
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
    def regions(self):
        regions = []

        # first region: header
        header = AuthorHeader(self.context)
        regions.append(LegacyRegion([LegacyArea([header])]))

        # second region: topics, bio, contact
        topics = AuthorTopics(self.context)
        bio = AuthorBio(self.context)
        contact = AuthorContact(self.context)
        regions.append(LegacyRegion([
                       LegacyArea([topics, bio], kind="major"),
                       LegacyArea([contact], kind="minor")]))

        # third region: texts, comments
        regions.append(LegacyRegion(
            self.areas_for_tab, kind='tabbed', tabs=self.tabs))

        return regions

    @zeit.web.reify
    def areas_for_tab(self):
        if is_paginated(self.context, self.request):
            return [self.area_articles]
        else:
            return [self.area_favourite_content, self.area_articles]

    @zeit.web.reify
    def area_favourite_content(self):
        return LegacyArea(
            [LegacyModule([c], layout='zon-small')
             for c in self.context.favourite_content],
            kind='ranking')

    @zeit.web.reify
    def area_articles(self):
        cp = zeit.content.cp.centerpage.CenterPage()
        cp.uniqueId = 'http://xml.zeit.de'
        area = cp.body.create_item('region').create_item('area')
        area.kind = 'ranking'
        area.automatic_type = 'query'
        area.raw_query = u'author:"{}" AND (type:article)'.format(
            self.context.display_name)
        area.raw_order = 'date-first-released desc'
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        area.count = int(conf.get('author_articles_page_size', '10'))
        area.automatic = True

        return AuthorArticleRanking(area, self.context)


class AuthorArticleRanking(zeit.web.site.area.ranking.Ranking):

    def __init__(self, context, author):
        super(AuthorArticleRanking, self).__init__(context)
        self.uids_above = [
            x.uniqueId for x in author.favourite_content]

    @zeit.web.reify
    def count(self):
        if self.page == 1:
            return self._count - len(self.uids_above)
        return self._count


@pyramid.view.view_config(
    renderer='templates/author.html',
    context=zeit.content.author.interfaces.IAuthor,
    name='kommentare')
class Comments(Author):

    current_tab_name = 'kommentare'

    @zeit.web.reify
    def areas_for_tab(self):
        return [LegacyArea([])]  # XXX not yet implemented
