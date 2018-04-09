# -*- coding: utf-8 -*-

import zeit.cms.interfaces

import zeit.web.site.view_article


def test_liveblog_advertising_in_article_enabled(application, dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/liveblog-no-collapse')
    view = zeit.web.site.view_article.Article(context, dummy_request)
    assert view.advertising_in_article_enabled


def test_liveblog_advertising_in_article_disabled(application, dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/liveblog-collapse')
    view = zeit.web.site.view_article.Article(context, dummy_request)
    assert not view.advertising_in_article_enabled


def test_liveblog_collapse_preceding_content(testbrowser):
    browser = testbrowser('/zeit-online/article/liveblog-collapse')
    liveblog = browser.cssselect('.liveblog')
    assert len(liveblog) == 1
    assert 'js-liveblog' in liveblog[0].get('class')
    assert not browser.cssselect('[itemprop="articleBody"] .ad-container')


def test_liveblog_show_preceding_content(testbrowser):
    browser = testbrowser('/zeit-online/article/liveblog-no-collapse')
    liveblog = browser.cssselect('.liveblog')
    assert len(liveblog) == 1
    assert 'js-liveblog' not in liveblog[0].get('class')
    assert browser.cssselect('[itemprop="articleBody"] .ad-container')
