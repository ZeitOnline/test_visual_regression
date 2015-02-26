# -*- coding: utf-8 -*-

import zeit.cms.interfaces


def test_article_should_render_full_view(testserver, testbrowser):
    article_path = '{}/zeit-online/article/zeit{}'
    browser = testbrowser(article_path.format(
        testserver.url, '/komplettansicht'))
    article = zeit.cms.interfaces.ICMSContent(
        article_path.format('http://xml.zeit.de', ''))
    assert len(browser.cssselect('p.paragraph')) == article.paragraphs


def test_article_full_view_has_no_pagination(testbrowser, testserver):
    select = testbrowser('{}/zeit-online/article/zeit/komplettansicht'.format(
        testserver.url)).cssselect

    assert len(select('.summary, .byline, .metadata')) == 3
    assert len(select('.article__pagination')) == 0


def test_article_with_pagination(testbrowser, testserver):
    browser = testbrowser('{}/zeit-online/article/zeit'.format(testserver.url))
    select = browser.cssselect
    nexttitle = select('.article__pagination__nexttitle')
    numbers = select('.article__pager__number')

    assert len(select('.summary, .byline, .metadata')) == 3
    assert len(select('.article__page-teaser')) == 0
    assert len(select('.article__pagination')) == 1
    assert len(nexttitle) == 1
    assert nexttitle[0].text.strip() == (
        u'Der Horror von Crystal wurzelt in der Normalität')
    assert len(numbers) == 5
    assert '--current' in (numbers[0].get('class'))


def test_article_pagination_active_state(testbrowser, testserver):
    select = testbrowser('{}/zeit-online/article/zeit/seite-3'.format(
        testserver.url)).cssselect

    assert len(select('.summary, .byline, .metadata')) == 0
    assert select('.article__page-teaser')[0].text.strip() == (
        u'Seite 3/5: Man wird schlank und lüstern')
    assert select('.article__pagination__nexttitle')[0].text.strip() == (
        u'Aus dem abenteuerlustigen Mädchen vom Dorf wurde ein Junkie')
    assert '--current' in (select('.article__pager__number')[2].get('class'))
