# coding: utf-8
import mock
import urllib

import zeit.web.campus.view
import zeit.web.campus.view_centerpage


def test_sharing_titles_differ_from_html_title(testbrowser):
    browser = testbrowser('/campus/article/common')
    view = zeit.web.campus.view.Base(mock.Mock(), mock.Mock())

    pagetitle = browser.cssselect('title')[0].text
    og_title = browser.cssselect(
        'meta[property="og:title"]')[0].get('content')
    twitter_title = browser.cssselect(
        'meta[name="twitter:title"]')[0].get('content')

    assert pagetitle.endswith(view.pagetitle_suffix)
    assert og_title + view.pagetitle_suffix == pagetitle
    assert twitter_title + view.pagetitle_suffix == pagetitle


def test_page_should_have_default_pagetitle(dummy_request):
    context = mock.Mock()
    context.title = None
    context.supertitle = None
    view = zeit.web.campus.view_centerpage.Centerpage(context, mock.Mock())
    assert view.pagetitle == zeit.web.campus.view.Base.seo_title_default
    assert view.social_pagetitle == zeit.web.campus.view.Base.seo_title_default


def test_page_should_have_default_pagedescription(dummy_request):
    context = mock.Mock()
    context.subtitle = None
    view = zeit.web.campus.view_centerpage.Centerpage(context, mock.Mock())
    assert view.pagedescription == zeit.web.campus.view.Base.seo_title_default


def test_ressort_literally_returns_correct_ressort(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/index')
    view = zeit.web.campus.view_centerpage.Centerpage(context, mock.Mock())
    assert view.ressort_literally == 'Campus'
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/article/simple')
    article_view = zeit.web.campus.view_article.Article(context, mock.Mock())
    assert article_view.ressort_literally == 'Campus'
