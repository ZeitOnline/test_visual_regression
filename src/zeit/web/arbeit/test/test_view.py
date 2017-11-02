# -*- coding: utf-8 -*-
import zeit.cms.interfaces

import zeit.web.core.interfaces


def test_zar_simple_arbeit_article_is_zar_content(application):
    article = zeit.cms.interfaces.ICMSContent(
        "http://xml.zeit.de/arbeit/article/simple")
    assert zeit.web.core.interfaces.IVertical(article) == 'zar'


def test_simple_arbeit_article_has_topic_links_from_cp(application):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/arbeit/index')
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/arbeit/article/simple')
    cp_topiclink = zeit.web.core.interfaces.ITopicLink(cp)
    assert len(cp_topiclink) > 0
    assert cp_topiclink == zeit.web.core.interfaces.ITopicLink(article)
