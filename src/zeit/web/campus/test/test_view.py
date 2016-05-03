# coding: utf-8
import mock

import zeit.web.campus.view
import zeit.web.campus.view_centerpage


def test_sharing_titles_differ_from_html_title(testbrowser):
    browser = testbrowser('/campus/article/common')
    view = zeit.web.campus.view.Base(mock.Mock(), mock.Mock())

    pagetitle = browser.cssselect('title')[0].text
    og_title = browser.cssselect(
        'meta[property="og:title"]')[0].attrib.get('content')
    twitter_title = browser.cssselect(
        'meta[name="twitter:title"]')[0].attrib.get('content')

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


def test_schema_org_publisher_mark_up(testbrowser):
    # @see https://developers.google.com/structured-data/rich-snippets/articles
    # #article_markup_properties
    browser = testbrowser('/campus/article/simple')
    publisher = browser.cssselect('[itemprop="publisher"]')[0]
    logo = publisher.cssselect('[itemprop="logo"]')[0]

    # check Organization
    assert publisher.get('itemtype') == 'http://schema.org/Organization'
    assert publisher.cssselect('[itemprop="name"]')[0].get('content') == (
        'ZEIT Campus')
    assert publisher.cssselect('[itemprop="url"]')[0].get('href') == (
        'http://localhost/campus/index')
    assert logo.get('itemtype') == 'http://schema.org/ImageObject'
    assert logo.cssselect('[itemprop="url"]')[0].get('content') == (
        'http://localhost/static/latest/images/'
        'structured-data-publisher-logo-zco.png')
    assert logo.cssselect('[itemprop="width"]')[0].get('content') == '347'
    assert logo.cssselect('[itemprop="height"]')[0].get('content') == '60'
