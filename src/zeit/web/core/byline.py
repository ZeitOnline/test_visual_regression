# -*- coding: utf-8 -*-
import itertools

import grokcore.component
import zope.interface

import zeit.content.article.interfaces
import zeit.content.link.interfaces

import zeit.web


class IByline(zope.interface.Interface):
    """A string representation of information on author, genre, location of a
    content object. This depends on the content object and where the byline is
    shown, e.g. bylines for content in a list of teaser modules (say, on a
    centerpage) look differently than the byline on a single page (say, on an
    article).
    """


@zeit.web.register_filter
def get_byline(content, name=u''):
    """Natural language byline for centerpage teasers and article heads.

    `name` specifies the type of byline. The default (unnamed) byline is for
    teaser. If no specific named byline is found, falls back to the default.
    """
    try:
        return zope.component.getAdapter(content, IByline, name=name)
    except (zope.component.ComponentLookupError, TypeError):
        if name:
            return zope.component.queryAdapter(content, IByline, default=())
        else:
            return ()


@grokcore.component.adapter(
    zeit.cms.content.interfaces.ICommonMetadata)
@grokcore.component.implementer(IByline)
class Byline(list):
    """Bylines are rendered as a nested list of macro names and data points.
    We expand this nested structure by iterating over the list and calling
    respective macros for each entry.
    This micro language helps us construct natural language authorship
    attributions for various contexts (teaser-level, articles, links).

    A byline descriptor might look a little like this:

    [('text', 'Ein Kommentar'),
     ('text', 'von'),
     ('enum', (('text', 'Edgar Example'),
               ('text', 'Tiffany Test')))]

    And render to a simple string like this:

    'Ein Kommentar von Edgar Example und Tiffany Test'

    The library of macros is located at zeit.web.core:inc/meta/byline.html
    """

    # TODO: This should be configured by an XMLSource. So far the given
    # Simple-XML-Source in vivi does not offer what we need.

    genres = {'glosse': 'eine',
              'kommentar': 'ein',
              'leserartikel': 'ein',
              'gastbeitrag': 'ein',
              'interview': 'ein'}

    max_authors = 3

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
    def get_location(author):
        # Since authors might be free-text, a location is not guaranteed
        return getattr(author, 'location', '') or None

    @staticmethod
    def expand_authors(authors):
        for author in authors:
            # Don't break because of missing .meta files or invalid references.
            # (Surprisingly common in older articles is referencing the folder
            # instead of the author's index.xml).
            if isinstance(author, basestring):
                yield 'text', author
            elif getattr(author.target, 'display_name', None):
                yield 'text', author.target.display_name

    @zeit.web.reify
    def authors(self):
        # Check for author objects associated with the context
        authors = filter(bool, getattr(self.context, 'authorships', ()))

        if not authors:
            # As a fallback, collect free-text author strings
            authors = filter(bool, getattr(self.context, 'authors', ()))

        # Pre-sort our authors by location, to improve clustering
        return sorted(authors, key=self.get_location)

    def groups(self):
        groups = ()
        # Restrict authors to the defined maximum amount
        authors = self.authors[:self.max_authors]

        if not authors:
            # Bail out if we don't have any authors at all
            self[:] = []
            return

        # Cluster authors by their location
        cluster = itertools.groupby(authors, self.get_location)
        for location, sublist in cluster:
            group = ('enum', tuple(self.expand_authors(sublist)))
            if location:
                group = ('csv', (group, ('text', location)))
            groups += (group,)

        # Unwrap the location groups if there only is one
        groups = ('enum', groups) if len(groups) > 1 else groups[0]

        if len(self.authors) > self.max_authors:
            # If the author list is capped, we don't want "a, b und c u.a.",
            # but "a, b, c u.a.".
            self.append(('csv', groups[1]))
            self.append(('text', u'u.a.'))
        else:
            self.append(groups)


@grokcore.component.adapter(
    zeit.content.link.interfaces.ILink)
@grokcore.component.implementer(IByline)
class LinkTeaserByline(Byline):

    def genre(self):
        pass


@grokcore.component.adapter(
    zeit.cms.content.interfaces.ICommonMetadata, name='main')
@grokcore.component.implementer(IByline)
class ArticleByline(Byline):

    max_authors = 21

    @staticmethod
    def expand_authors(authors):
        for author in authors:
            if isinstance(author, basestring):
                yield 'text', author
            elif author.target.uniqueId:
                yield 'linked_author', author.target
            else:
                yield 'plain_author', author.target


@grokcore.component.adapter(
    zeit.cms.content.interfaces.ICommonMetadata, name='author')
@grokcore.component.implementer(IByline)
class StructuredDataByline(Byline):

    @staticmethod
    def expand_authors(authors):
        for author in authors:
            if isinstance(author, basestring):
                yield 'text', author
            else:
                yield 'plain_author', author.target


@grokcore.component.adapter(
    # XXX We'd rather use the class `LaxyProxy`, but that seems to have not
    # enough specificity.
    zeit.web.core.utils.ILazyProxy)
@grokcore.component.implementer(IByline)
class ProxyByline(Byline):

    def __init__(self, context):
        # Skip Byline.__init__(), we don't want to expose the proxy by probing
        # for properties it might not have.
        super(Byline, self).__init__()
        self.context = context
        self.from_()
        self.groups()

    @zeit.web.reify
    def authors(self):
        authors = filter(bool, self.context.__proxy__.get('authors', ()))
        return sorted(authors)


@grokcore.component.adapter(
    zeit.web.core.utils.ILazyProxy, name='author')
@grokcore.component.implementer(IByline)
class ProxyAuthorByline(ProxyByline, StructuredDataByline):
    pass
