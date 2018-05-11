# -*- coding: utf-8 -*-
import mock
import zeit.cms.interfaces
import zeit.web.core.interfaces


def test_zar_simple_arbeit_article_is_zar_content(application):
    article = zeit.cms.interfaces.ICMSContent(
        "http://xml.zeit.de/arbeit/article/simple")
    assert zeit.web.core.interfaces.IVertical(article) == 'zar'


def test_zar_simple_article_has_topic_links_from_cp(application):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/arbeit/index')
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/arbeit/article/simple')
    cp_topiclink = zeit.web.core.interfaces.ITopicLink(cp)
    assert len(cp_topiclink) > 0
    assert cp_topiclink == zeit.web.core.interfaces.ITopicLink(article)


def test_zar_ressort_literally_returns_correct_ressort(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/arbeit/index')
    view = zeit.web.arbeit.view_centerpage.Centerpage(context, mock.Mock())
    assert view.ressort_literally == 'Arbeit'
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/arbeit/article/simple')
    article_view = zeit.web.arbeit.view_article.Article(context, mock.Mock())
    assert article_view.ressort_literally == 'Arbeit'
