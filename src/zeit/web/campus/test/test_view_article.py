# -*- coding: utf-8 -*-
import pytest

import zeit.cms.interfaces


@pytest.mark.skipif(True,
                    reason="Waiting for ZON-2835: Article blocks #1616")
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
