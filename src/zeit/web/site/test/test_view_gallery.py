# -*- coding: utf-8 -*-

import zeit.cms.interfaces


def test_article_should_render_full_view(testserver, testbrowser):
    article_path = '{}/zeit-online/article/zeit{}'
    browser = testbrowser(article_path.format(
        testserver.url, '/komplettansicht'))
    article = zeit.cms.interfaces.ICMSContent(
        article_path.format('http://xml.zeit.de', ''))
    assert len(browser.cssselect('p.paragraph')) == article.paragraphs


def test_zon_gallery_should_have_metadata(testbrowser, testserver):
    select = testbrowser('{}/zeit-online/gallery/biga_1'.format(
        testserver.url)).cssselect
    assert len(select('.summary, .byline, .metadata')) == 3


def test_zon_gallery_should_have_no_pagination(testbrowser, testserver):
    select = testbrowser('{}/zeit-online/gallery/biga_1'.format(
        testserver.url)).cssselect
    assert len(select('.pagination')) == 0


def test_zon_gallery_should_have_description(testbrowser, testserver):
    select = testbrowser('{}/zeit-online/gallery/biga_1'.format(
        testserver.url)).cssselect
    assert len(select('.gallery__description')) == 1


def test_zon_gallery_should_display_a_gallery(testbrowser, testserver):
    select = testbrowser('{}/zeit-online/gallery/biga_1'.format(
        testserver.url)).cssselect
    assert len(select('.gallery')) == 1
