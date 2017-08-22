# -*- coding: utf-8 -*-
import logging

import zeit.content.article.interfaces
import zeit.content.gallery.interfaces
import zeit.content.video.interfaces

import zeit.web
import zeit.web.core.article
import zeit.web.core.view


log = logging.getLogger(__name__)


@zeit.web.view_defaults(
    vertical='zar',
    renderer='zeit.web.arbeit:templates/inc/comments/thread.html',
    name='comment-thread')
@zeit.web.view_config(context=zeit.content.article.interfaces.IArticle)
@zeit.web.view_config(context=zeit.content.gallery.interfaces.IGallery)
@zeit.web.view_config(context=zeit.content.video.interfaces.IVideo)
@zeit.web.view_config(context=zeit.web.core.article.ILiveblogArticle)
@zeit.web.view_config(context=zeit.web.core.article.IColumnArticle)
class CommentThread(
        zeit.web.core.view.CommentMixin, zeit.web.core.view.Base):
    pass