# -*- coding: utf-8 -*-
import logging

import pyramid.view

import zeit.web.core
import zeit.web.core.view
import zeit.web.magazin.view


log = logging.getLogger(__name__)


@pyramid.view.view_defaults(
    renderer='zeit.web.magazin:templates/inc/comments/thread.html',
    name='comment-thread',
    custom_predicates=(zeit.web.magazin.view.is_zmo_content,))
@pyramid.view.view_config(context=zeit.content.article.interfaces.IArticle)
@pyramid.view.view_config(context=zeit.content.gallery.interfaces.IGallery)
@pyramid.view.view_config(context=zeit.content.video.interfaces.IVideo)
@pyramid.view.view_config(context=zeit.web.core.article.ILiveblogArticle)
@pyramid.view.view_config(context=zeit.web.core.article.IShortformArticle)
@pyramid.view.view_config(context=zeit.web.core.article.IColumnArticle)
@pyramid.view.view_config(context=zeit.web.core.article.IPhotoclusterArticle)
class CommentThread(
        zeit.web.core.view.CommentMixin, zeit.web.core.view.Base):
    pass