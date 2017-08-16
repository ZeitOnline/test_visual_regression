# -*- coding: utf-8 -*-
import pytest


def test_zar_article_single_page_has_no_pagination(testbrowser):
    select = testbrowser('/arbeit/article/simple').cssselect

    assert len(select('.summary, .byline, .metadata')) == 3
    assert len(select('.article-pagination')) == 1
    assert len(select('.article-pager')) == 0
    assert len(select('.article-toc')) == 0


def test_zar_article_full_view_has_no_pagination(testbrowser):
    select = testbrowser('/arbeit/article/paginated/komplettansicht').cssselect

    assert len(select('.summary, .byline, .metadata')) == 2
    assert len(select('.article-pagination')) == 1
    assert len(select('.article-pager')) == 0
    assert len(select('.article-toc')) == 0


def test_zar_article_paginated_has_toc(testbrowser):
    browser = testbrowser('/arbeit/article/paginated/')
    toc = browser.cssselect('.article-toc')
    assert len(toc) == 1


def test_zar_article_renders_quotes_correctly(testbrowser):
    browser = testbrowser('/arbeit/article/quotes')
    quotes = browser.cssselect('.quote')
    arrows = browser.cssselect('.quote__source-arrow')
    assert len(quotes) == 4
    assert len(arrows) == 2


@pytest.mark.parametrize('c1_parameter', [
    '?C1-Meter-Status=paywall&C1-Meter-User-Status=anonymous',
    '?C1-Meter-Status=paywall&C1-Meter-User-Status=registered',
    '?C1-Meter-Status=always_paid'])
def test_zar_paywall_switch_showing_forms(c1_parameter, testbrowser):
    urls = [
        'arbeit/article/paginated',
        'arbeit/article/paginated/seite-2',
        'arbeit/article/paginated/komplettansicht',
        'arbeit/article/simple'
    ]

    for url in urls:
        browser = testbrowser(
            '{}{}'.format(url, c1_parameter))
        assert len(browser.cssselect('.paragraph--faded')) == 1
        assert len(browser.cssselect('.gate')) == 1
        assert len(browser.cssselect(
            '.gate--register')) == int('anonymous' in c1_parameter)


def test_zar_article_zplus_comments_under_register_article(testbrowser):
    c1_param = '?C1-Meter-Status=paywall&C1-Meter-User-Status=anonymous'
    path = '/arbeit/article/comments'
    url = '{}{}'.format(path, c1_param)
    browser = testbrowser(url)

    assert len(browser.cssselect('.paragraph--faded')) == 1
    assert len(browser.cssselect('.gate')) == 1
    assert len(browser.cssselect('.comment-section')) == 1


def test_zar_article_zplus_comments_not_under_abo_article(testbrowser):
    c1_param = '?C1-Meter-Status=always_paid'
    path = '/arbeit/article/comments'
    url = '{}{}'.format(path, c1_param)
    browser = testbrowser(url)

    assert len(browser.cssselect('.comment-section')) == 0


def test_zar_article_paginated_has_headerimage_only_on_first_page(testbrowser):
    browser = testbrowser('/arbeit/article/01-digitale-nomaden/')
    assert len(browser.cssselect('.article__media--header-image')) == 1

    browser = testbrowser('/arbeit/article/01-digitale-nomaden/seite-2')
    assert not browser.cssselect('.article__media--header-image')

    browser = testbrowser(
        '/arbeit/article/01-digitale-nomaden/komplettansicht')
    assert len(browser.cssselect('.article__media--header-image')) == 1


def test_zar_article_image_has_caption(testbrowser):
    browser = testbrowser('/arbeit/article/01-digitale-nomaden')
    headerimage = browser.cssselect('figure.article__media--header-image')
    assert len(headerimage) == 1
    headerimage_caption = headerimage[0].cssselect('.figure__text')
    assert len(headerimage_caption) == 1
    assert headerimage_caption[0].text.strip().startswith('Freiheit')


def test_zar_article_toc_has_fallback_title(testbrowser):
    browser = testbrowser('/arbeit/article/paginated-nopagetitle/seite-2')

    toc_items = browser.cssselect('.article-toc__item')
    assert len(toc_items) == 4

    toc_item_1 = toc_items[0].cssselect('span')[0]
    assert toc_item_1.text.strip() == 'Mehrseitiger Artikel ohne Seiten-Titel'

    toc_item_2 = toc_items[1].cssselect('span')[0]
    assert toc_item_2.text.strip() == 'Seite 2'


def test_zar_article_with_dark_header_has_correct_structure(testbrowser):
    browser = testbrowser('/arbeit/article/header-dark')
    # we want to see one header, which has a modifier
    assert len(browser.cssselect('.article-header--dark')) == 1
    # the article heading items are inside the header-container
    assert len(browser.cssselect(
        '.article-header--dark > .article-heading')) == 1
    # image should be outside/behind the header (because the figure caption
    # has a bright background)
    assert len(browser.cssselect(
        '.article-header--dark + .article__media--header-image')) == 1


def test_zar_article_header_on_second_page_has_correct_structure(testbrowser):
    browser = testbrowser('/arbeit/article/header-dark/seite-2')
    assert len(browser.cssselect('.article-header--dark')) == 1
    assert len(browser.cssselect(
        '.article-header--dark .article__page-teaser')) == 1
    assert len(browser.cssselect('.article__media--header-image')) == 0
