# -*- coding: utf-8 -*-


def test_breadcrumbs_should_produce_markup(testbrowser):
    # @see https://developers.google.com/structured-data/breadcrumbs
    browser = testbrowser('/artikel/03')
    breadcrumb = browser.cssselect('[itemprop="breadcrumb"]')[0]
    elements = breadcrumb.cssselect('[itemprop="itemListElement"]')
    items = breadcrumb.cssselect('[itemprop="item"]')
    names = breadcrumb.cssselect('[itemprop="name"]')
    positions = breadcrumb.cssselect('[itemprop="position"]')

    # check Organization
    assert breadcrumb.get('itemtype') == 'http://schema.org/BreadcrumbList'
    assert elements[0].get('itemtype') == 'http://schema.org/ListItem'
    assert items[0].get('href') == 'http://localhost/'
    assert names[0].get('content') == 'ZEIT ONLINE'
    assert positions[0].get('content') == '1'
    assert len(elements) == 4
    assert len(items) == 3
    assert len(names) == 4
    assert len(positions) == 4
