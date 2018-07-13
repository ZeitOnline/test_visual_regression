# -*- coding: utf-8 -*-


def test_article_contains_required_structured_data(testbrowser):
    # @see https://developers.google.com/structured-data/rich-snippets/articles
    data = testbrowser('/zeit-magazin/article/01').structured_data()

    page = data['WebPage']
    article = data['Article']
    publisher = data['Organization']
    breadcrumb = data['BreadcrumbList']

    # check WebPage
    assert page['publisher']['@id'] == publisher['@id']
    assert page['breadcrumb']['@id'] == breadcrumb['@id']

    # check Organization
    assert publisher['@id'] == '#publisher'
    assert publisher['name'] == 'ZEITmagazin'
    assert publisher['url'] == 'http://localhost/zeit-magazin/index'
    assert publisher['logo']['@type'] == 'ImageObject'
    assert publisher['logo']['url'] == (
        'http://localhost/static/latest/images/'
        'structured-data-publisher-logo-zmo.png')
    assert publisher['logo']['width'] == 600
    assert publisher['logo']['height'] == 56

    # check BreadcrumbList
    assert len(breadcrumb['itemListElement']) == 5

    for index, item in enumerate(breadcrumb['itemListElement'], start=1):
        assert item['@type'] == 'ListItem'
        assert item['position'] == index
        if index == 1:
            assert item['item']['@id'] == 'http://localhost/'
            assert item['item']['name'] == 'ZEIT ONLINE'
        elif index == 2:
            assert item['item']['@id'] == 'http://localhost/archiv'
            assert item['item']['name'] == 'DIE ZEIT Archiv'
        elif index == 5:
            assert item['name'] == u'Gentrifizierung: Mei, is des traurig!'

    # check Article
    assert article['mainEntityOfPage']['@id'] == (
        'http://localhost/zeit-magazin/article/01')
    assert article['headline'] == u'Gentrifizierung: Mei, is des traurig!'
    assert len(article['description'])
    assert article['datePublished'] == '2013-09-26T08:00:00+02:00'
    assert article['dateModified'] == '2013-10-08T11:25:03+02:00'
    assert article['keywords'] == (
        u'Gentrifizierung, Christian Ude, Facebook, Mietvertrag, München')
    assert article['publisher']['@id'] == publisher['@id']

    # check ImageObject
    assert article['image']['@type'] == 'ImageObject'
    assert article['image']['url'] == (
        'http://localhost/exampleimages/artikel/01/schoppenstube/'
        'wide__1300x731')
    assert article['image']['width'] == 1300
    assert article['image']['height'] == 731

    # check author
    assert article['author']['@type'] == 'Person'
    assert article['author']['name'] == 'Anne Mustermann'
    assert article['author']['url'] == (
        'http://localhost/autoren/anne_mustermann')


def test_series_article_contains_required_structured_data(testbrowser):
    data = testbrowser('/zeit-magazin/article/03').structured_data()

    serie = data['Article']['isPartOf']

    assert serie['@type'] == 'WebPage'
    assert serie['@id'] == 'http://localhost/serie/weinkolumne'
    assert serie['name'] == 'Weinkolumne'


def test_abo_article_contains_required_structured_data(testbrowser):
    browser = testbrowser('/zeit-magazin/article/zplus-zmo-paid')
    data = browser.structured_data()

    article = data['Article']

    assert article['isAccessibleForFree'] == 'False'
    assert article['hasPart']['@type'] == 'WebPageElement'
    assert article['hasPart']['isAccessibleForFree'] == 'False'
    assert article['hasPart']['cssSelector'] == 'main .article-page'


def test_free_article_contains_required_structured_data(testbrowser):
    data = testbrowser('/zeit-magazin/article/03').structured_data()

    article = data['Article']

    assert 'isAccessibleForFree' not in article
    assert 'hasPart' not in article


def test_seriespage_contains_required_structured_data(testbrowser, data_solr):
    data = testbrowser('/serie/martenstein').structured_data()

    page = data['WebPage']
    itemlist = data['ItemList']
    publisher = data['Organization']
    breadcrumb = data['BreadcrumbList']

    # check WebPage
    assert page['publisher']['@id'] == publisher['@id']
    assert page['breadcrumb']['@id'] == breadcrumb['@id']

    # check Organization
    assert publisher['@id'] == '#publisher'
    assert publisher['name'] == 'ZEITmagazin'
    assert publisher['url'] == 'http://localhost/zeit-magazin/index'
    assert publisher['logo']['@type'] == 'ImageObject'
    assert publisher['logo']['url'] == (
        'http://localhost/static/latest/images/'
        'structured-data-publisher-logo-zmo.png')
    assert publisher['logo']['width'] == 600
    assert publisher['logo']['height'] == 56

    # check BreadcrumbList
    assert len(breadcrumb['itemListElement']) == 3

    for index, item in enumerate(breadcrumb['itemListElement'], start=1):
        assert item['@type'] == 'ListItem'
        assert item['position'] == index
        if index == 1:
            assert item['item']['@id'] == 'http://localhost/'
            assert item['item']['name'] == 'ZEIT ONLINE'
        elif index == 2:
            assert item['item']['@id'] == 'http://localhost/zeit-magazin/index'
            assert item['item']['name'] == 'ZEITmagazin'
        elif index == 3:
            assert item['name'] == 'Serie: Martenstein'

    # check ItemList
    assert len(itemlist['itemListElement']) == 5

    for index, item in enumerate(itemlist['itemListElement'], start=1):
        assert item['@type'] == 'ListItem'
        assert item['position'] == index
