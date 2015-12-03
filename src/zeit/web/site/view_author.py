import pyramid.view

import zeit.content.author.interfaces

from zeit.web.site.view_centerpage import LegacyArea, LegacyRegion
import zeit.web.site.view


@zeit.web.register_module('author_header')
class AuthorHeader(zeit.web.site.module.Module):

    def __init__(self, context):
        super(AuthorHeader, self).__init__(context)
        self.layout = 'author_header'


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


@zeit.web.register_module('author_comments')
class AuthorComments(zeit.web.site.module.Module):

    def __init__(self, context):
        super(AuthorComments, self).__init__(context)
        self.layout = 'author_comments'

    pass


@zeit.web.register_module('author_texts')
class AuthorTexts(zeit.web.site.module.Module):

    def __init__(self, context):
        super(AuthorTexts, self).__init__(context)
        self.layout = 'author_texts'

    pass


@pyramid.view.view_config(
    renderer='templates/author.html',
    context=zeit.content.author.interfaces.IAuthor)
class Author(zeit.web.core.view.Base):

    advertising_enabled = True

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
        texts = AuthorTexts(self.context)
        comments = AuthorComments(self.context)
        regions.append(LegacyRegion([
                       LegacyArea([texts]), LegacyArea([comments])]))

        return regions
