# -*- coding: utf-8 -*-

import zeit.cms.interfaces

import zeit.web.campus.view_article


def test_article_should_render_full_view(testbrowser):
    browser = testbrowser('/campus/article/paginated/komplettansicht')
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/article/paginated')
    assert len(browser.cssselect(
        '.article-page > p.paragraph')) == article.paragraphs


def test_article_pagination_on_single_page(testbrowser):
    select = testbrowser('/campus/article/simple').cssselect

    assert len(select('.article-header')) == 1
    assert len(select('.article-pagination')) == 1
    assert len(select('.article-pagination__nexttitle')) == 0
    assert len(select('.article-pager')) == 0
    # assert len(select('.article-toc')) == 0
    button = select('.article-pagination__button')[0]
    assert button.text.strip() == 'Startseite'


def test_article_pagination_on_second_page(testbrowser):
    select = testbrowser('/campus/article/paginated/seite-2').cssselect

    assert len(select('.article-header')) == 0
    assert len(select('.page-header')) == 1
    assert len(select('.article-pagination')) == 1
    assert len(select('.article-pagination__nexttitle')) == 1
    assert len(select('.article-pager')) == 1
    # assert len(select('.article-toc')) == 1
    button = select('.article-pagination__button')[0]
    assert button.text.strip() == u'Nächste Seite'


def test_article_pagination_on_last_paginated_page(testbrowser):
    select = testbrowser('/campus/article/paginated/seite-9').cssselect

    assert len(select('.article-header')) == 0
    assert len(select('.page-header')) == 1
    assert len(select('.article-pagination')) == 1
    assert len(select('.article-pagination__nexttitle')) == 0
    assert len(select('.article-pager')) == 1
    # assert len(select('.article-toc')) == 1
    button = select('.article-pagination__button')[0]
    assert button.text.strip() == 'Startseite'


def test_article_pagination_on_komplettansicht(testbrowser):
    select = testbrowser('/campus/article/paginated/komplettansicht').cssselect

    assert len(select('.article-header')) == 1
    assert len(select('.article-pagination')) == 1
    assert len(select('.article-pagination__nexttitle')) == 0
    assert len(select('.article-pager')) == 0
    # assert len(select('.article-toc')) == 0
    button = select('.article-pagination__button')[0]
    assert button.text.strip() == 'Startseite'


def test_article_pagination(testbrowser):
    select = testbrowser('/campus/article/paginated').cssselect
    numbers = select('.article-pager__number')

    assert len(select('.article-header')) == 1
    assert len(select('.page-header')) == 0
    assert len(select('.article-pagination')) == 1
    assert select('.article-pagination__nexttitle')[0].text.strip() == (
        u'Polaroid-Drucker, VR-Brillen, E-Reader, DJ-Kabel und das Hoverboard')
    assert len(numbers) == 7
    assert '--current' in numbers[0].get('class')
    assert numbers[5].text_content().strip() == u'…'
    # assert len(select('.article-toc')) == 1
    # assert len(select('.article-toc__item')) == 5
    # assert '--current' in select('.article-toc__item')[0].get('class')


def test_article_citation_block_should_render_expected_structure(testbrowser):
    browser = testbrowser('/campus/article/citation')
    assert len(browser.cssselect('.quote')) == 2
    assert browser.cssselect('.quote__text')[0].text.startswith(
        u'Es war ein Gedankenanstoß')
    assert browser.cssselect('.quote__source')[0].text_content() == (
        'Ariane Jedlitschka, Kunstschaffende')
    assert browser.cssselect('.quote__link')[0].get('href') == (
        'http://www.imdb.com/title/tt0110912/quotes?item=qt0447099')
    # 'imdb.com' in browser.cssselect('.quote')[0].attrib['cite']


def test_article_should_render_topicpagelink(testbrowser):
    browser = testbrowser('/campus/article/common')
    tplink = browser.cssselect('.article-header__topicpagelink')[0]
    assert tplink.text == 'Science'
    assert tplink.get('href') == 'http://localhost/thema/test'


def test_article_should_have_topicpagelink_fallback_label(
        monkeypatch, testbrowser):
    monkeypatch.setattr(zeit.campus.article.TopicpageLink, 'label', '')
    browser = testbrowser('/campus/article/common')
    tplink = browser.cssselect('.article-header__topicpagelink')[0]
    assert tplink.text == 'Test-Thema'


def test_article_should_not_render_missing_topicpagelink(
        monkeypatch, testbrowser):
    monkeypatch.setattr(
        zeit.web.campus.view_article.Article, 'topicpagelink_label', '')
    browser = testbrowser('/campus/article/common')
    tplink = browser.cssselect('.article-header__topicpagelink')
    assert len(tplink) == 0


def test_article_tags_are_present(testbrowser):
    browser = testbrowser('/campus/article/simple')
    assert browser.cssselect('nav.article-tags')
    tags = browser.cssselect('a.article-tags__link')
    assert len(tags) == 6
    for tag in tags:
        assert tag.get('rel') == 'tag'
