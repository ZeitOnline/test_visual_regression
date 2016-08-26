# -*- coding: utf-8 -*-
import logging

import pyramid.httpexceptions
import pyramid.view

import zeit.cms.interfaces

import zeit.web.core
import zeit.web.core.comments
import zeit.web.core.metrics
import zeit.web.core.security
import zeit.web.core.template
import zeit.web.core.view
import zeit.web.site.view
import zeit.web.campus.view


log = logging.getLogger(__name__)


@pyramid.view.view_defaults(
    renderer='zeit.web.campus:templates/inc/comments/thread.html',
    name='comment-thread',
    custom_predicates=(zeit.web.campus.view.is_zco_content,))
@pyramid.view.view_config(context=zeit.content.article.interfaces.IArticle)
@pyramid.view.view_config(context=zeit.content.gallery.interfaces.IGallery)
@pyramid.view.view_config(context=zeit.content.video.interfaces.IVideo)
@pyramid.view.view_config(context=zeit.web.core.article.ILiveblogArticle)
@pyramid.view.view_config(context=zeit.web.core.article.IShortformArticle)
@pyramid.view.view_config(context=zeit.web.core.article.IColumnArticle)
@pyramid.view.view_config(context=zeit.web.core.article.IPhotoclusterArticle)
class CommentThreadCampus(
        zeit.web.core.view.CommentMixin, zeit.web.core.view.Base):
    pass
