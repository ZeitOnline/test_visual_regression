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
    sources = browser.cssselect('.quote__source')
    assert len(quotes) == 4
    assert len(sources) == 2


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
