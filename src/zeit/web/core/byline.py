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
        authors = filter(bool, getattr(self.context, 'authorships', ()))

        if not authors:
            authors = filter(bool, getattr(self.context, 'authors', ()))
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


@grokcore.component.adapter(
    zeit.content.link.interfaces.ILink)
@grokcore.component.implementer(IByline)
class LinkTeaserByline(Byline):

    def genre(self):
        pass


@grokcore.component.adapter(
    zeit.cms.content.interfaces.ICommonMetadata, name='article')
@grokcore.component.implementer(IByline)
class ArticleByline(Byline):

    @staticmethod
    def expand_authors(authors):
        for author in authors:
            if author.target.uniqueId:
                yield 'linked_author', author.target
            else:
                yield 'plain_author', author.target


@grokcore.component.adapter(
    zeit.content.cp.interfaces.IStoryStream, name='article')
@grokcore.component.implementer(IByline)
class StorystreamByline(ArticleByline):
    pass


@grokcore.component.adapter(
    zeit.cms.content.interfaces.ICommonMetadata, name='author')
@grokcore.component.implementer(IByline)
class StructuredDataByline(Byline):

    @staticmethod
    def expand_authors(authors):
        for author in authors:
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
        authors = filter(bool, self.context.__proxy__.get('authors', ()))
        if authors:
            self.from_()
            authors = tuple(('text', a) for a in authors)
            self.append(('enum', authors))
