# -*- coding: utf-8 -*-


def test_breadcrumbs_should_produce_markup(testbrowser):
    browser = testbrowser('/zeit-magazin/article/03')
    breadcrumb = browser.cssselect('.breadcrumbs__list')[0]
    items = breadcrumb.cssselect('.breadcrumbs__item')
    links = breadcrumb.cssselect('.breadcrumbs__link')

    assert len(items) == 4
    assert len(links) == 3

    assert links[0].get('href') == 'http://localhost/index'
    assert links[0].get('title') == 'ZEIT ONLINE'
    assert links[0].text == 'Start'
    assert items[3].text == (
        'Kolumne Die Ausleser: Der Chianti hat eine zweite Chance verdient')


def test_breadcrumbs_should_produce_required_structured_data(testbrowser):
    data = testbrowser('/zeit-magazin/article/03').structured_data()
    page = data['WebPage']
    breadcrumb = data['BreadcrumbList']
    itemlist = breadcrumb['itemListElement']

    assert page['breadcrumb']['@id'] == breadcrumb['@id']
    assert len(itemlist) == 4

    for index, item in enumerate(itemlist, start=1):
        assert item['@type'] == 'ListItem'
        assert item['position'] == index
        if index == 4:
            assert item['name'] == (
                'Kolumne Die Ausleser: '
                'Der Chianti hat eine zweite Chance verdient')
        else:
            assert item['item']['@id'].startswith('http://localhost/')
            assert 'name' in item['item']
