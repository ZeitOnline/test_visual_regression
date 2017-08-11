"""Marker interfaces for ZMO articles with certain templates"""
import zeit.content.article.interfaces


class ILongformArticle(zeit.content.article.interfaces.IArticle):
    """XXX Note that there are ZON-longform articles that reside in /feature
    which are marked with IZMOContent since longform rendering is performed
    by zeit.web.magazin for historical reasons; the whole "longform" topic
    needs to be overhauled.
    """


class IShortformArticle(zeit.content.article.interfaces.IArticle):
    pass


class IColumnArticle(zeit.content.article.interfaces.IArticle):
    pass


class IPhotoclusterArticle(zeit.content.article.interfaces.IArticle):
    pass
