# -*- coding: utf-8 -*-
import mock

import zeit.cms.interfaces

import zeit.web.core.banner
import zeit.web.core.template
import zeit.web.magazin


def test_banner_toggles_viewport_zoom(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/02')
    view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert view.banner_toggles('viewport_zoom') == 'tablet-landscape'


def test_banner_should_not_be_displayed_on_short_pages(testbrowser):
    browser = testbrowser('/zeit-magazin/article/header-traum')
    assert not browser.cssselect('#iqadtile4')


def test_banner_should_not_be_displayed_on_disabled_article(testbrowser):
    # test article with xml banner = no
    browser = testbrowser('/zeit-magazin/article/nobanner')
    # no desktop ads
    assert not browser.cssselect('div[class*="ad-tile_"]')


def test_banner_should_not_be_displayed_on_disabled_cp(testbrowser):
    # centerpage without ads
    browser = testbrowser('/zeit-magazin/centerpage/index-without-ads')
    # no desktop ads
    assert not browser.cssselect('div[class*="ad-tile_"]')


def test_banner_tile7_should_appear_on_article_pages(testbrowser):
    browser = testbrowser('/zeit-magazin/article/03')
    assert browser.cssselect('#ad-desktop-7')
    browser = testbrowser('/zeit-magazin/article/03/seite-3')
    assert browser.cssselect('#ad-desktop-7')
    browser = testbrowser('/zeit-magazin/article/03/seite-4')
    assert browser.cssselect('#ad-desktop-7')
    browser = testbrowser('/zeit-magazin/article/03/seite-7')
    assert browser.cssselect('#ad-desktop-7')


def test_banner_tile3_should_be_displayed_on_pages(testbrowser):
    browser = testbrowser('/zeit-magazin/article/01')
    assert browser.cssselect('#ad-desktop-3')
    browser = testbrowser('/zeit-magazin/centerpage/lebensart')
    assert browser.cssselect('#ad-desktop-3')


def test_banner_tile7_should_not_appear_on_short_pages(testbrowser):
    browser = testbrowser('/zeit-magazin/article/03/seite-2')
    assert not browser.cssselect('#ad-desktop-7')
    browser = testbrowser('/zeit-magazin/article/03/seite-5')
    assert not browser.cssselect('#ad-desktop-7')
    browser = testbrowser('/zeit-magazin/article/03/seite-6')
    assert not browser.cssselect('#ad-desktop-7')
