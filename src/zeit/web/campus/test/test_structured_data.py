# -*- coding: utf-8 -*-


def test_article_contains_required_structured_data(testbrowser):
    # @see https://developers.google.com/structured-data/rich-snippets/articles
    data = testbrowser('/campus/article/common').structured_data()

    page = data['WebPage']
    article = data['Article']
    publisher = data['Organization']
    breadcrumb = data['BreadcrumbList']

    # check WebPage
    assert page['publisher']['@id'] == publisher['@id']
    assert page['breadcrumb']['@id'] == breadcrumb['@id']

    # check Organization
    assert publisher['@id'] == '#publisher'
    assert publisher['name'] == 'ZEIT Campus'
    assert publisher['url'] == 'http://localhost/campus/index'
    assert publisher['logo']['@type'] == 'ImageObject'
    assert publisher['logo']['url'] == (
        'http://localhost/static/latest/images/'
        'structured-data-publisher-logo-zco.png')
    assert publisher['logo']['width'] == 347
    assert publisher['logo']['height'] == 60

    # check BreadcrumbList
    assert len(breadcrumb['itemListElement']) == 3

    for index, item in enumerate(breadcrumb['itemListElement'], start=1):
        assert item['@type'] == 'ListItem'
        assert item['position'] == index
        if index == 1:
            assert item['item']['@id'] == 'http://localhost/'
            assert item['item']['name'] == 'ZEIT ONLINE'
        elif index == 2:
            assert item['item']['@id'] == 'http://localhost/campus/index'
            assert item['item']['name'] == 'ZEIT Campus'
        elif index == 3:
            assert item['name'] == u'"Der Hobbit": Geht\'s noch größer?'

    # check Article
    assert article['mainEntityOfPage']['@id'] == (
        'http://localhost/campus/article/common')
    assert article['headline'] == u'"Der Hobbit": Geht\'s noch größer?'
    assert len(article['description'])
    assert article['datePublished'] == '2016-02-09T08:36:17+01:00'
    assert article['dateModified'] == '2016-02-10T10:39:16+01:00'
    assert article['keywords'] == (
        u'Student, Hochschule, Auslandssemester, Bafög-Antrag, Praktikum, '
        u'Studienfinanzierung')
    assert article['publisher']['@id'] == publisher['@id']

    # check ImageObject
    assert article['image']['@type'] == 'ImageObject'
    assert article['image']['url'] == (
        'http://localhost/campus/image/jura-studium-fleiss/wide__1300x731')
    assert article['image']['width'] == 1300
    assert article['image']['height'] == 731

    # check author
    assert article['author']['@type'] == 'Person'
    assert article['author']['name'] == 'Wenke Husmann'
    assert article['author']['url'] == (
        'http://localhost/autoren/H/Wenke_Husmann/index.xml')


def test_series_article_contains_required_structured_data(testbrowser):
    data = testbrowser('/campus/article/common').structured_data()

    serie = data['Article']['isPartOf']

    assert serie['@type'] == 'WebPage'
    assert serie['@id'] == 'http://localhost/serie/in-der-mensa-mit'
    assert serie['name'] == 'In der Mensa mit'


def test_abo_article_contains_required_structured_data(testbrowser):
    data = testbrowser('/campus/article/common').structured_data()

    article = data['Article']

    assert article['isAccessibleForFree'] == 'False'
    assert article['hasPart']['@type'] == 'WebPageElement'
    assert article['hasPart']['isAccessibleForFree'] == 'False'
    assert article['hasPart']['cssSelector'] == 'main .article-page'


def test_free_article_contains_required_structured_data(testbrowser):
    data = testbrowser('/campus/article/simple').structured_data()

    article = data['Article']

    assert 'isAccessibleForFree' not in article
    assert 'hasPart' not in article
