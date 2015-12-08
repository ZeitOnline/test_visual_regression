import pyramid.view

import zeit.content.author.interfaces

from zeit.web.site.view_centerpage import LegacyArea
from zeit.web.site.view_centerpage import LegacyModule
from zeit.web.site.view_centerpage import LegacyRegion


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
            [self.area_for_tab], kind='tabbed', tabs=self.tabs))

        # fourth region: pinned and automatic teasers
        ranking = LegacyArea([LegacyModule([c], layout='zon-small') for c in
                              self.context.favourite_content], kind='ranking')
        regions.append(LegacyRegion([ranking]))

        return regions

    @zeit.web.reify
    def area_for_tab(self):
        return LegacyArea([])  # XXX not yet implemented


@pyramid.view.view_config(
    renderer='templates/author.html',
    context=zeit.content.author.interfaces.IAuthor,
    name='kommentare')
class Comments(Author):

    current_tab_name = 'kommentare'

    @zeit.web.reify
    def area_for_tab(self):
        return LegacyArea([])  # XXX not yet implemented
