# -*- coding: utf-8 -*-
from mock import Mock
from zeit.frontend import view  # NOQA
from zeit.frontend import view_article
from zeit.frontend.banner import Place
from zope.testbrowser.browser import Browser
import pytest
import zeit.cms.interfaces


def test_banner_place_should_be_serialized(testserver):
    place = Place(1, ['728x90'], True, label='')
    assert place.__dict__ == {'dcopt': 'ist', 'diuqilon': True,
                              'label': '', 'min_width': 0, 'name': 'tile_1',
                              'noscript_width_height': ['728', '90'],
                              'sizes': ['728x90'], 'tile': 1}


def test_banner_place_should_raise_on_index_error(testserver):
    with pytest.raises(IndexError):
        Place(1, '123x456', True, label='')


def test_banner_list_should_be_sorted(testserver):
    tiles = [place.tile for place in zeit.frontend.banner.banner_list]
    assert sorted(tiles) == tiles


def test_banner_view_should_return_Place_if_tile_present(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/02')
    article_view = view_article.Article(context, Mock())
    assert isinstance(article_view.banner(1), zeit.frontend.banner.Place)


def test_banner_view_should_return_None_if_tile_is_not_present(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/02')
    article_view = view_article.Article(context, Mock())
    assert article_view.banner(999) is None


def test_banner_should_not_be_displayed_on_short_pages(testserver):
    browser = Browser('%s/artikel/header2' % testserver.url)
    assert '<div id="iqadtile4" class="ad__tile_4 ad__width_300">' \
        not in browser.contents


def test_banner_should_not_be_displayed_on_disabled_pages(testserver):
    browser = Browser('%s/artikel/05' % testserver.url)
    assert '<div id="iqadtile4" class="ad__tile_4 ad__width_300">' \
        not in browser.contents


def test_banner_view_should_be_displayed_on_pages(testserver):
    browser = Browser('%s/artikel/03' % testserver.url)
    assert ('<div id="iqadtile7" class="ad__tile_7 ad__on__article '
            'ad__width_300 ad__min__768">') in browser.contents
    assert ('<div id="iqadtile8" class="ad__tile_8 ad__on__article '
            'ad__width_300 ad__min__768">') in browser.contents
    browser = Browser('%s/artikel/03/seite-3' % testserver.url)
    assert ('<div id="iqadtile7" class="ad__tile_7 ad__on__article '
            'ad__width_300 ad__min__768">') in browser.contents
    browser = Browser('%s/artikel/03/seite-4' % testserver.url)
    assert ('<div id="iqadtile7" class="ad__tile_7 ad__on__article '
            'ad__width_300 ad__min__768">') in browser.contents
    browser = Browser('%s/artikel/03/seite-7' % testserver.url)
    assert ('<div id="iqadtile7" class="ad__tile_7 ad__on__article '
            'ad__width_300 ad__min__768">') in browser.contents


def test_banner_tile3_should_be_displayed_on_pages(testserver):
    browser = Browser('%s/artikel/01' % testserver.url)
    assert ('<div id="iqadtile3" class="ad__tile_3 ad__on__article '
            'ad__width_800 ad__min__768">') in browser.contents
    browser = Browser('%s/centerpage/lebensart' % testserver.url)
    assert ('<div id="iqadtile3" class="ad__tile_3 ad__on__centerpage '
            'ad__width_800 ad__min__768">') in browser.contents


def test_banner_view_should_be_displayed_on_succeeding_pages(testserver):
    browser = Browser('%s/artikel/03/seite-2' % testserver.url)
    assert ('<div id="iqadtile7" class="ad__tile_7 ad__on__article '
            'ad__width_300 ad__min__768">') not in browser.contents
    browser = Browser('%s/artikel/03/seite-5' % testserver.url)
    assert ('<div id="iqadtile7" class="ad__tile_7 ad__on__article '
            'ad__width_300 ad__min__768">') not in browser.contents
    browser = Browser('%s/artikel/03/seite-6' % testserver.url)
    assert ('<div id="iqadtile7" class="ad__tile_7 ad__on__article '
            'ad__width_300 ad__min__768">') not in browser.contents


def test_banner_mobile_should_request_with_correct_data(testserver):
    browser = Browser('%s/artikel/01' % testserver.url)
    assert "var sas_pageid = '32375/445608'" in browser.contents
    assert "sas_formatid = 13500," in browser.contents
