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
    assert len(select('.pagination')) == 0


def test_article_with_pagination(testbrowser, testserver):
    browser = testbrowser('{}/zeit-online/article/zeit'.format(testserver.url))
    select = browser.cssselect
    nexttitle = select('.pagination__nexttitle')
    numbers = select('.pager__number')

    assert len(select('.summary, .byline, .metadata')) == 3
    assert len(select('.article__page-teaser')) == 0
    assert len(select('.pagination')) == 1
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
    assert select('.pagination__nexttitle')[0].text.strip() == (
        u'Aus dem abenteuerlustigen Mädchen vom Dorf wurde ein Junkie')
    assert '--current' in (select('.pager__number')[2].get('class'))


def test_breaking_news_article_renders_breaking_bar(testbrowser, testserver):
    select = testbrowser('{}/zeit-online/article/eilmeldungsartikel'.format(
        testserver.url)).cssselect

    assert len(select('.breaking-news-banner')) == 1
    assert len(select('.article-heading--breaking-news')) == 1


def test_schema_org_mainContentOfPage(testbrowser, testserver):
    select = testbrowser('{}/zeit-online/article/01'.format(
        testserver.url)).cssselect

    assert len(select('main[itemprop="mainContentOfPage"]')) == 1


def test_schema_org_Article(testbrowser, testserver):
    select = testbrowser('{}/zeit-online/article/01'.format(
        testserver.url)).cssselect

    assert len(select(
        'article[itemtype="http://schema.org/Article"][itemscope]')) == 1


def test_schema_org_headline(testbrowser, testserver):
    select = testbrowser('{}/zeit-online/article/01'.format(
        testserver.url)).cssselect
    headline = select('h1[itemprop="headline"]')
    text = u'"Der Hobbit": Geht\'s noch gr\xf6\xdfer?'
    assert len(headline) == 1
    assert text in headline[0].text_content()


def test_schema_org_description(testbrowser, testserver):
    select = testbrowser('{}/zeit-online/article/01'.format(
        testserver.url)).cssselect

    assert len(select('div[itemprop="description"]')) == 1


def test_schema_org_author(testbrowser, testserver):
    select = testbrowser('{}/zeit-online/article/01'.format(
        testserver.url)).cssselect

    assert len(select('.byline[itemprop="author"]')) == 1
    assert len(select('.byline a[itemprop="url"]')) == 1
    assert len(select('.byline span[itemprop="name"]')) == 1


def test_schema_org_articleBody(testbrowser, testserver):
    select = testbrowser('{}/zeit-online/article/01'.format(
        testserver.url)).cssselect

    assert len(select('.article-body[itemprop="articleBody"]')) == 1


def test_schema_org_image(testbrowser, testserver):
    select = testbrowser('{}/zeit-online/article/01'.format(
        testserver.url)).cssselect
    json = 'article > script[type="application/ld+json"]'
    assert(len(select(json))) == 1
