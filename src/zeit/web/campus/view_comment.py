# -*- coding: utf-8 -*-
import logging

import zeit.content.article.interfaces
import zeit.content.gallery.interfaces
import zeit.content.video.interfaces

import zeit.web
import zeit.web.campus.view
import zeit.web.core.article
import zeit.web.core.view


log = logging.getLogger(__name__)


@zeit.web.view_defaults(
    renderer='zeit.web.campus:templates/inc/comments/thread.html',
    name='comment-thread',
    custom_predicates=(zeit.web.campus.view.is_zco_content,))
@zeit.web.view_config(context=zeit.content.article.interfaces.IArticle)
@zeit.web.view_config(context=zeit.content.gallery.interfaces.IGallery)
@zeit.web.view_config(context=zeit.content.video.interfaces.IVideo)
@zeit.web.view_config(context=zeit.web.core.article.ILiveblogArticle)
@zeit.web.view_config(context=zeit.web.core.article.IShortformArticle)
@zeit.web.view_config(context=zeit.web.core.article.IColumnArticle)
@zeit.web.view_config(context=zeit.web.core.article.IPhotoclusterArticle)
class CommentThread(
        zeit.web.core.view.CommentMixin, zeit.web.core.view.Base):
    pass
