# -*- coding: utf-8 -*-
import logging

import grokcore.component
import zope.interface

class IRenderByline(zope.interface.Interface):

    """A string representation of information on
    author, genre, location of a ICMSContent resource
    """

@grokcore.component.implementer(IRenderByline)
@grokcore.component.adapter(zeit.cms.interfaces.ICMSContent)
class RenderByline(object):

    genre = ['glosse', 'reportage', 'nachricht', 'analyse']
    eine_n = lambda x: 'eine' if x in self.gernre else 'ein'
    byline = []

    def __init__(self, content):
        self.byline.append(self.eine_n(content.grenre))
        self.byline.append(content.genre.title())
        self.byline.append('von')

        if content.genre == 'interview':
            self.byline = [].append('Interview:')

        authors = filter(lambda a: a is not None, content.authorships)
        for author in authors:
            byline.append(Author(author))
            byline.append(',')
            if last(author):
                byline = byline[:-1]
                byline[-2] = 'und'

class Author(object):

    def __init__(self, obj):
        self.display_name = obj.display_name
        self.href = self.uniqueId

    def __str__(self):
        return self.display_name

    def render(self, html):
        return html.format((self.display_name, self.uniqueId)

