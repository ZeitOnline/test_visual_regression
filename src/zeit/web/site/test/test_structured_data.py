# -*- coding: utf-8 -*-


def test_article_contains_required_structured_data(testbrowser):
    # @see https://developers.google.com/structured-data/rich-snippets/articles
    data = testbrowser('/zeit-online/article/amp').structured_data()

    page = data['WebPage']
    article = data['Article']
    publisher = data['Organization']
    breadcrumb = data['BreadcrumbList']

    # check WebPage
    assert page['publisher']['@id'] == publisher['@id']
    assert page['breadcrumb']['@id'] == breadcrumb['@id']

    # check Organization
    assert publisher['@id'] == '#publisher'
    assert publisher['name'] == 'ZEIT ONLINE'
    assert publisher['url'] == 'http://localhost/index'
    assert publisher['logo']['@type'] == 'ImageObject'
    assert publisher['logo']['url'] == (
        'http://localhost/static/latest/images/'
        'structured-data-publisher-logo-zon.png')
    assert publisher['logo']['width'] == 565
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
            assert item['item']['@id'] == 'http://localhost/wirtschaft/index'
            assert item['item']['name'] == 'Wirtschaft'
        elif index == 3:
            assert item['name'] == u'Flüchtlinge: Mehr Davos, weniger Kreuth'

    # check Article
    assert article['mainEntityOfPage']['@id'] == (
        'http://localhost/zeit-online/article/amp')
    assert article['headline'] == u'Flüchtlinge: Mehr Davos, weniger Kreuth'
    assert len(article['description'])
    assert article['datePublished'] == '2016-01-22T11:55:46+01:00'
    assert article['dateModified'] == '2016-01-22T11:55:46+01:00'
    assert article['keywords'] == (
        u'Flüchtling, Weltwirtschaftsforum Davos, '
        u'Arbeitsmarkt, Migration, Europäische Union')
    assert article['publisher']['@id'] == publisher['@id']

    # check ImageObject
    assert article['image']['@type'] == 'ImageObject'
    assert article['image']['url'] == (
        'http://localhost/zeit-online/image/'
        'filmstill-hobbit-schlacht-fuenf-hee/wide__1300x731')
    assert article['image']['width'] == 1300
    assert article['image']['height'] == 731

    # check author
    assert article['author']['@type'] == 'Person'
    assert article['author']['name'] == 'Jochen Wegner'
    assert article['author']['url'] == (
        'http://localhost/autoren/W/Jochen_Wegner/index')


def test_series_article_contains_required_structured_data(testbrowser):
    data = testbrowser('/zeit-online/article/fischer').structured_data()

    serie = data['Article']['isPartOf']

    assert serie['@type'] == 'WebPage'
    assert serie['@id'] == 'http://localhost/serie/fischer-im-recht'
    assert serie['name'] == 'Fischer im Recht'


def test_abo_article_contains_required_structured_data(testbrowser):
    data = testbrowser('/zeit-online/article/zplus-zeit').structured_data()

    article = data['Article']

    assert article['isAccessibleForFree'] == 'False'
    assert article['hasPart']['@type'] == 'WebPageElement'
    assert article['hasPart']['isAccessibleForFree'] == 'False'
    assert article['hasPart']['cssSelector'] == 'main .article-page'


def test_free_article_contains_required_structured_data(testbrowser):
    data = testbrowser('/zeit-online/article/simple').structured_data()

    article = data['Article']

    assert 'isAccessibleForFree' not in article
    assert 'hasPart' not in article
