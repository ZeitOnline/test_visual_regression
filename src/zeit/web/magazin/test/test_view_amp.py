# -*- coding: utf-8 -*-


def test_amp_view_should_have_expected_structure(testbrowser):
    browser = testbrowser('/amp/artikel/01')
    link = browser.cssselect('head link[rel="canonical"]')[0]
    article = browser.cssselect('article.article')[0]
    image = article.cssselect('figure.figure')[0]

    assert ('<html ⚡ lang="de" itemscope '
            'itemtype="http://schema.org/WebPage">') in browser.contents
    assert link.get('href') == 'http://localhost/artikel/01'
    assert 'figure--large' in image.get('class')


def test_amp_contains_required_microdata(testbrowser):
    browser = testbrowser('/amp/artikel/01')
    publisher = browser.document.get_element_by_id('publisher')
    logo = publisher.cssselect('[itemprop="logo"]')[0]

    article = browser.cssselect('article[itemprop="mainEntity"]')[0]
    main_entity_of_page = article.cssselect('[itemprop="mainEntityOfPage"]')[0]
    headline = article.cssselect('[itemprop="headline"]')[0]
    description = article.cssselect('[itemprop="description"]')[0]
    date_published = article.cssselect('[itemprop="datePublished"]')[0]
    date_modified = article.cssselect('[itemprop="dateModified"]')[0]
    author = article.cssselect('[itemprop="author"]')[0]
    image = article.cssselect('[itemprop="image"]')[0]
    copyright_holder = image.cssselect('[itemprop="copyrightHolder"]')[0]

    # check Organization of Page
    assert publisher.get('itemtype') == 'http://schema.org/Organization'
    assert publisher.cssselect('[itemprop="name"]')[0].get('content') == (
        'ZEITmagazin')
    assert publisher.cssselect('[itemprop="url"]')[0].get('href') == (
        'http://localhost/zeit-magazin/index')
    assert logo.get('itemtype') == 'http://schema.org/ImageObject'
    assert logo.cssselect('[itemprop="url"]')[0].get('content') == (
        'http://localhost/static/latest/images/'
        'structured-data-publisher-logo-zmo.png')
    assert logo.cssselect('[itemprop="width"]')[0].get('content') == '600'
    assert logo.cssselect('[itemprop="height"]')[0].get('content') == '56'

    # check Article
    assert article.get('itemtype') == 'http://schema.org/Article'
    assert main_entity_of_page.get('content') == (
        'http://localhost/artikel/01')
    text = headline.text_content().strip()
    assert text == u'Gentrifizierung: Mei, is des traurig!'
    assert len(description.text_content().strip())

    # reassign publisher
    publisher = article.cssselect('[itemprop="publisher"]')[0]
    logo = publisher.cssselect('[itemprop="logo"]')[0]

    # check Organization of Article
    assert publisher.get('itemtype') == 'http://schema.org/Organization'
    assert publisher.cssselect('[itemprop="name"]')[0].get('content') == (
        'ZEITmagazin')
    assert publisher.cssselect('[itemprop="url"]')[0].get('content') == (
        'http://localhost/zeit-magazin/index')
    assert logo.get('itemtype') == 'http://schema.org/ImageObject'
    assert logo.cssselect('[itemprop="url"]')[0].get('content') == (
        'http://localhost/static/latest/images/'
        'structured-data-publisher-logo-zmo.png')
    assert logo.cssselect('[itemprop="width"]')[0].get('content') == '600'
    assert logo.cssselect('[itemprop="height"]')[0].get('content') == '56'

    # check ImageObject
    assert image.get('itemtype') == 'http://schema.org/ImageObject'
    assert len(image.cssselect('[itemprop="url"]')[0].get('content'))
    assert image.cssselect('[itemprop="width"]')[0].get('content') == '820'
    assert image.cssselect('[itemprop="height"]')[0].get('content') == '548'
    assert len(image.cssselect('[itemprop="caption"]')) == 1
    assert copyright_holder.get('itemtype') == 'http://schema.org/Person'
    url = copyright_holder.cssselect('[itemprop="url"]')[0]
    person = copyright_holder.cssselect('[itemprop="name"]')[0]
    assert url.get('href') == 'http://foo.de'
    assert person.text == u'© Andreas Gebert/dpa'

    assert date_published.get('datetime') == '2013-09-26T08:00:00+02:00'
    assert date_modified.get('datetime') == '2013-10-08T11:25:03+02:00'

    assert author.get('itemtype') == 'http://schema.org/Person'
    assert author.cssselect('[itemprop="name"]')[0].text == 'Anne Mustermann'
    assert author.cssselect('[itemprop="url"]')[0].get('href') == (
        'http://localhost/autoren/anne_mustermann')
