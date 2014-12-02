# -*- coding: utf-8 -*-

import grokcore.component
import zope.interface

import zeit.content.article.interfaces
import zeit.content.link.interfaces

import zeit.web


class IRenderByline(zope.interface.Interface):

    """A string representation of information on
    author, genre, location of a ICMSContent resource
    """


@zeit.web.register_filter
def render_byline(resource):
    """Extract a natural language byline composited of authors and locations.
    The returned object sports an __html__ method and is jinja serializable.

    :param article: Article providing zeit.content.article.IArticle
    :rtype: zeit.web.core.byline.IRenderByline
    """
    try:
        return unicode(IRenderByline(resource))
    except TypeError:
        return ''


@grokcore.component.implementer(IRenderByline)
@grokcore.component.adapter(zeit.content.article.interfaces.IArticle)
class RenderByline(object):
    # ToDo: This should be configured by a XMLSource
    # So far the given Simple-XML-Source in vivi does not offer
    # what we need.
    genre = ['glosse', 'reportage', 'nachricht', 'analyse']
    display_fe = ['glosse', 'kommentar', 'leserartikel', 'gastbeitrag',
                  'interview']
    eine_n = lambda self, x: 'Eine ' if x in self.genre else 'Ein '

    def __init__(self, content):
        self.byline = []
        self._genre(content)
        self._von(content)
        self._interview_exception(content)
        self._author_str(content)

    def __unicode__(self):
        return ''.join(unicode(x[0]) + x[1] if isinstance(x, tuple)
                       else str(x) for x in self.byline)

    def __str__(self):
        return unicode(self.byline).encode('utf-8')

    def __html__(self):
        return unicode(self.byline)

    def _genre(self, content):
        if getattr(content, 'genre', '') in self.display_fe:
            self.byline.append(self.eine_n(content.genre))
            self.byline.append(content.genre.title() + ' ')

    def _von(self, content):
        if self.byline:
            self.byline.append('von ')
        else:
            self.byline.append('Von ')

    def _interview_exception(self, content):
        if (getattr(content, 'genre', '') in self.display_fe and
                getattr(content, 'genre', '') == 'interview'):
            self.byline = ['%s: ' % content.genre.title()]

    def _author_str(self, content):
        authors = filter(lambda a: a is not None, content.authorships)

        if not authors:  # we don't have a byline, if we have no authors for it
            self.byline = []
            return

        authors_str, authors_location = self._author_location_list(authors)
        zipped = zip(authors_str, authors_location)

        # insert punctation and remove last ', '
        punctation = [', ' for x in authors_str]
        zipped = list(sum(zip(zipped, punctation), ()))[:-1]

        # insert conjunction
        if len(zipped) > 1:
            zipped[-2] = ' und '  # whitespace is relevant

        # append authors list to byline
        self.byline += zipped

    def _author_location_list(self, authors):
        authors_str = [Author(a) for a in authors]
        authors_location = [', ' + author.location if author.location else ''
                            for author in authors]

        if len(set(authors_location)) == 1:
            authors_location = (['' for x in range(len(authors_location) - 1)]
                                + [authors_location[0]])

        assert len(authors_str) == len(authors_location)
        return authors_str, authors_location


@grokcore.component.implementer(IRenderByline)
@grokcore.component.adapter(zeit.content.link.interfaces.ILink)
class RenderLinkByline(RenderByline):

    def __init__(self, content):
        self.byline = []
        self._von(content)
        self._interview_exception(content)
        self._author_str(content)


@grokcore.component.implementer(IRenderByline)
@grokcore.component.adapter(zeit.content.gallery.interfaces.IGallery)
class RenderGalleryByline(RenderByline):
    pass


class Author(object):

    def __init__(self, obj):

        self.name = obj.target.display_name
        self.href = obj.target.uniqueId

    def __unicode__(self):
        return self.name

    def __str__(self):
        return unicode(self.name).encode('utf-8')

    def render(self, html):
        return html.format((self.name, self.uniqueId))
