# -*- coding: utf-8 -*-


def test_amp_view_should_have_expected_structure(testbrowser):
    browser = testbrowser('/amp/campus/article/common')
    link = browser.cssselect('head link[rel="canonical"]')[0]
    article = browser.cssselect('article.article')[0]
    image = article.cssselect('figure.figure')[0]

    assert ('<html ⚡ lang="de" itemscope '
            'itemtype="http://schema.org/WebPage">') in browser.contents
    assert link.get('href') == 'http://localhost/campus/article/common'
    assert 'figure--large' in image.get('class')


def test_amp_contains_required_microdata(testbrowser):
    browser = testbrowser('/amp/campus/article/common')
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
        'ZEIT Campus')
    assert publisher.cssselect('[itemprop="url"]')[0].get('href') == (
        'http://localhost/campus/index')
    assert logo.get('itemtype') == 'http://schema.org/ImageObject'
    assert logo.cssselect('[itemprop="url"]')[0].get('content') == (
        'http://localhost/static/latest/images/'
        'structured-data-publisher-logo-zco.png')
    assert logo.cssselect('[itemprop="width"]')[0].get('content') == '347'
    assert logo.cssselect('[itemprop="height"]')[0].get('content') == '60'

    # check Article
    assert article.get('itemtype') == 'http://schema.org/Article'
    assert main_entity_of_page.get('content') == (
        'http://localhost/campus/article/common')
    text = headline.text_content().strip()
    assert text == u'"Der Hobbit": Geht\'s noch größer?'
    assert len(description.text_content().strip())

    # reassign publisher
    publisher = article.cssselect('[itemprop="publisher"]')[0]
    logo = publisher.cssselect('[itemprop="logo"]')[0]

    # check Organization of Article
    assert publisher.get('itemtype') == 'http://schema.org/Organization'
    assert publisher.cssselect('[itemprop="name"]')[0].get('content') == (
        'ZEIT Campus')
    assert publisher.cssselect('[itemprop="url"]')[0].get('content') == (
        'http://localhost/campus/index')
    assert logo.get('itemtype') == 'http://schema.org/ImageObject'
    assert logo.cssselect('[itemprop="url"]')[0].get('content') == (
        'http://localhost/static/latest/images/'
        'structured-data-publisher-logo-zco.png')
    assert logo.cssselect('[itemprop="width"]')[0].get('content') == '347'
    assert logo.cssselect('[itemprop="height"]')[0].get('content') == '60'

    # check ImageObject
    assert image.get('itemtype') == 'http://schema.org/ImageObject'
    assert image.cssselect('[itemprop="url"]')[0].get('content') == (
        'http://localhost/campus/image/jura-studium-fleiss/portrait__612x816')
    assert image.cssselect('[itemprop="width"]')[0].get('content') == '612'
    assert image.cssselect('[itemprop="height"]')[0].get('content') == '816'
    assert len(image.cssselect('[itemprop="caption"]')) == 1
    assert copyright_holder.get('itemtype') == 'http://schema.org/Person'
    url = copyright_holder.cssselect('[itemprop="url"]')[0]
    person = copyright_holder.cssselect('[itemprop="name"]')[0]
    assert url.get('href').startswith('http://www.photocase.de/')
    assert person.text == u'© Rike./photocase.de'

    assert date_published.get('datetime') == '2016-02-09T08:36:17+01:00'
    assert date_modified.get('datetime') == '2016-02-10T10:39:16+01:00'

    assert author.get('itemtype') == 'http://schema.org/Person'
    assert author.cssselect('[itemprop="name"]')[0].text == 'Wenke Husmann'
    assert author.cssselect('[itemprop="url"]')[0].get('href') == (
        'http://localhost/autoren/H/Wenke_Husmann/index.xml')
