# -*- coding: utf-8 -*-
import itertools

import grokcore.component
import zope.interface

import zeit.content.article.interfaces
import zeit.content.cp.interfaces
import zeit.content.link.interfaces

import zeit.web


class ITeaserByline(zope.interface.Interface):
    """A string representation of information on author, genre, location of a
    ICMSContent resource to be displayed in a teaser context.
    """


class IContentByline(zope.interface.Interface):
    """A string representation of information on author, genre, location of a
    ICMSContent resource to be displayed on a content page.
    """


@zeit.web.register_ctxfilter
def get_byline(context, content):
    """Natural language byline for centerpage teasers and article heads."""
    context = getattr(context.get('view'), 'context', None)
    if zeit.content.cp.interfaces.ICenterPage.providedBy(context):
        return ITeaserByline(content, ())
    return IContentByline(content, ())


class Byline(list):

    # TODO: This should be configured by an XMLSource. So far the given
    # Simple-XML-Source in vivi does not offer what we need.

    genres = {'glosse': 'eine',
              'kommentar': 'ein',
              'leserartikel': 'ein',
              'gastbeitrag': 'ein',
              'interview': 'ein'}

    def __init__(self, context):
        super(Byline, self).__init__()
        self.context = context
        self.genre()
        self.from_()
        self.interview()
        self.column()
        self.groups()

    def __repr__(self):
        return object.__repr__(self)

    def genre(self):
        if getattr(self.context, 'genre', None) in self.genres:
            prefix = self.genres.get(self.context.genre, 'ein')
            genre = u'{} {}'.format(prefix, self.context.genre).title()
            self.append(('text', genre))

    def from_(self):
        self.append(('text', u'von' if self else u'Von'))

    def interview(self):
        if getattr(self.context, 'genre', None) == 'interview':
            # Replace any prior byline efforts with a special interview label.
            self[:] = [('text', u'{}:'.format(self.context.genre.title()))]

    def column(self):
        if getattr(self.context, 'serie', None) and self.context.serie.column:
            # Replace any prior byline efforts with a special interview label.
            self[:] = [('text', u'Eine Kolumne von ')]

    @staticmethod
    def expand_authors(authors):
        for author in authors:
            # Don't break because of missing .meta files or invalid references.
            # (Surprisingly common in older articles is referencing the folder
            # instead of the author's index.xml).
            display_name = getattr(author.target, 'display_name', None)
            if not display_name:
                continue
            yield 'text', display_name

    def groups(self):
        authors = filter(bool, self.context.authorships)

        if not authors:
            authors = filter(bool, self.context.authors)
            if not authors:
                self[:] = []  # Bail out if we don't have any authors.
            else:
                authors = tuple(('text', a) for a in authors)
                self.append(('enum', authors))
            return

        def get_loc(author):
            return author.location or None

        groups = ()
        cluster = itertools.groupby(sorted(authors, key=get_loc), get_loc)
        for location, sublist in cluster:
            group = ('enum', tuple(self.expand_authors(sublist)))
            if location:
                group = ('csv', (group, ('text', location)))
            groups += (group,)

        self.append(('enum', groups) if len(groups) > 1 else groups[0])


@grokcore.component.implementer(ITeaserByline)
@grokcore.component.adapter(zeit.cms.content.interfaces.ICommonMetadata)
class TeaserByline(Byline):
    pass


@grokcore.component.implementer(ITeaserByline)
@grokcore.component.adapter(zeit.content.link.interfaces.ILink)
class LinkTeaserByline(TeaserByline):

    def genre(self):
        pass


@grokcore.component.implementer(IContentByline)
@grokcore.component.adapter(zeit.cms.content.interfaces.ICommonMetadata)
class ContentByline(Byline):
    pass


@grokcore.component.implementer(IContentByline)
@grokcore.component.adapter(zeit.content.article.interfaces.IArticle)
class ArticleContentByline(ContentByline):

    @staticmethod
    def expand_authors(authors):
        for author in authors:
            if author.target.uniqueId:
                yield 'linked_author', author.target
            else:
                yield 'plain_author', author.target
