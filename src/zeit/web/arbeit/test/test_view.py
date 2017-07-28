# -*- coding: utf-8 -*-
import zeit.cms.interfaces
import zeit.web.arbeit.view


def test_zar_simple_arbeit_article_is_zar_content(application):
    article = zeit.cms.interfaces.ICMSContent(
        "http://xml.zeit.de/arbeit/article/simple")
    assert zeit.web.arbeit.view.is_zar_content(article, None)
