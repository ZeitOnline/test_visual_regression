# -*- coding: utf-8 -*-

import datetime

import zeit.cms.interfaces

import zeit.web.site.view_article


def test_liveblog_advertising_in_article_enabled(application, dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/liveblog-no-collapse')
    view = zeit.web.site.view_article.Article(context, dummy_request)
    assert view.advertising_in_article_body_enabled


def test_liveblog_advertising_in_article_disabled(application, dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/liveblog-collapse')
    view = zeit.web.site.view_article.Article(context, dummy_request)
    assert not view.advertising_in_article_body_enabled


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


def test_liveblog_has_no_print_menu(testbrowser):
    browser = testbrowser('/zeit-online/article/liveblog3')
    assert not browser.cssselect('.sharing-menu__item--printbutton')
    assert not browser.cssselect('.print-menu')


def test_liveblog_updates_modified_date(testbrowser):
    browser = testbrowser('/zeit-online/liveblog/sonnenfinsternis')
    select = browser.cssselect
    date_published = select('time[itemprop="datePublished"]')[0]
    date_modified = select('time[itemprop="dateModified"]')[0]

    assert select('meta[name="date"]')[0].get('content') == (
        '2015-03-20T12:26:00+01:00')
    assert select('meta[name="last-modified"]')[0].get('content') == (
        '2015-03-20T12:26:00+01:00')
    assert select('.liveblog-status__meta-date')[0].text == u'20. März 2015'
    assert date_published.get('datetime') == '2015-03-20T12:26:00+01:00'
    assert date_published.text == u'20. März 2015, 12:26 Uhr'
    assert date_modified.get('datetime') == '2015-03-20T12:26:00+01:00'
    assert date_modified.text == u'Aktualisiert am 20. März 2015, 12:26 Uhr'


def test_liveblog_v3_updates_modified_date(testbrowser):
    browser = testbrowser('/zeit-online/article/liveblog3')
    select = browser.cssselect
    date_published = select('time[itemprop="datePublished"]')[0]
    date_modified = select('time[itemprop="dateModified"]')[0]

    assert select('meta[name="date"]')[0].get('content') == (
        '2018-06-02T15:31:50+02:00')
    assert select('meta[name="last-modified"]')[0].get('content') == (
        '2018-06-02T15:31:50+02:00')
    assert select('.liveblog-status__meta-date')[0].text == '2. Juni 2018'
    assert date_published.get('datetime') == '2018-06-02T15:31:50+02:00'
    assert date_published.text == '2. Juni 2018, 15:31 Uhr'
    assert date_modified.get('datetime') == '2018-06-02T15:31:50+02:00'
    assert date_modified.text == 'Aktualisiert am 2. Juni 2018, 15:31 Uhr'


def test_liveblog_teaser_updates_modified_date(testbrowser, clock):
    clock.freeze(datetime.datetime(2015, 3, 20, 13, 28))
    browser = testbrowser('/zeit-online/journalistic-formats-liveblog')
    articles = browser.cssselect('article[data-unique-id$="sonnenfinsternis"]')

    assert articles

    for article in articles:
        time = article.cssselect('time')[0]
        assert time.get('datetime') == '2015-03-20T12:26:00+01:00'
        assert time.text == 'Vor 2 Stunden'
