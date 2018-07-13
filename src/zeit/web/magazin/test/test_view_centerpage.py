# -*- coding: utf-8 -*-


def test_zmo_teasers_have_series_label(testbrowser):
    browser = testbrowser('/zeit-magazin/centerpage/teasers-to-series')
    select = browser.cssselect
    assert len(select('.teaser-fullwidth__series-label')) == 1
    assert len(select('.teaser-square-large__series-label')) == 1
    assert len(select('.teaser-landscape-large')) == 1
    assert len(select('.teaser-landscape-large-photo__series-label')) == 1
    assert len(select('.teaser-landscape-small__series-label')) == 2
    assert len(select('.teaser-upright-large__series-label')) == 1
    assert len(select('.card__series-label')) == 3
    assert len(select('.teaser-upright__series-label')) == 1

    assert len(select('.teaser-mtb-square')) == 3
    assert len(select('.teaser-mtb-square__series-label')) == 0


def test_zmo_topicpage_contains_required_structured_data(
        testbrowser, data_solr):
    data = testbrowser('/zeit-magazin/centerpage/tube').structured_data()

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
            assert item['name'] == 'Thema: Teaserliste'

    # check ItemList
    assert len(itemlist['itemListElement']) == 5

    for index, item in enumerate(itemlist['itemListElement'], start=1):
        assert item['@type'] == 'ListItem'
        assert item['position'] == index
