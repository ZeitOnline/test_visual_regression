# -*- coding: utf-8 -*-
import pytest


def test_amp_contains_required_microdata(testbrowser, testserver):
    browser = testbrowser('/amp/zeit-online/article/amp')
    publisher = browser.cssselect('[itemprop="publisher"]')[0]
    logo = publisher.cssselect('[itemprop="logo"]')[0]

    article = browser.cssselect('article[itemprop="mainEntity"]')[0]
    mainEntityOfPage = article.cssselect('[itemprop="mainEntityOfPage"]')[0]
    headline = article.cssselect('[itemprop="headline"]')[0]
    description = article.cssselect('[itemprop="description"]')[0]
    datePublished = article.cssselect('[itemprop="datePublished"]')[0]
    dateModified = article.cssselect('[itemprop="dateModified"]')[0]
    author = article.cssselect('[itemprop="author"]')[0]

    image = article.cssselect('[itemprop="image"]')[0]
    copyrightHolder = image.cssselect('[itemprop="copyrightHolder"]')[0]

    # check Organization
    assert publisher.get('itemtype') == 'http://schema.org/Organization'
    assert publisher.cssselect('[itemprop="name"]')[0].get('content') == (
        'ZEIT ONLINE')
    assert publisher.cssselect('[itemprop="url"]')[0].get('href') == (
        testserver.url + '/index')
    assert logo.get('itemtype') == 'http://schema.org/ImageObject'
    assert logo.cssselect('[itemprop="url"]')[0].get('content') == (
        testserver.url + '/static/latest/images/'
        'structured-data-publisher-logo-zon.png')
    assert logo.cssselect('[itemprop="width"]')[0].get('content') == '565'
    assert logo.cssselect('[itemprop="height"]')[0].get('content') == '60'

    # check Article
    assert article.get('itemtype') == 'http://schema.org/Article'
    assert mainEntityOfPage.get('href') == (
        testserver.url + '/zeit-online/article/amp')
    text = headline.text_content().strip()
    assert text.startswith(u'Flüchtlinge: ')
    assert text.endswith(u'Mehr Davos, weniger Kreuth')
    assert len(description.text_content().strip())

    # check ImageObject
    assert image.get('itemtype') == 'http://schema.org/ImageObject'
    assert image.cssselect('[itemprop="url"]')[0].get('content') == (
        testserver.url + '/zeit-online/image/'
        'filmstill-hobbit-schlacht-fuenf-hee/wide__822x462')
    assert image.cssselect('[itemprop="width"]')[0].get('content') == '660'
    assert image.cssselect('[itemprop="height"]')[0].get('content') == '371'
    assert len(image.cssselect('[itemprop="caption"]')) == 1
    assert copyrightHolder.get('itemtype') == 'http://schema.org/Person'
    person = copyrightHolder.cssselect('[itemprop="name"]')[0]
    assert person.text == u'© Warner Bros.'

    assert datePublished.get('datetime') == '2016-01-22T11:55:46+01:00'
    assert dateModified.get('datetime') == '2016-01-22T11:55:46+01:00'

    assert author.get('itemtype') == 'http://schema.org/Person'
    assert author.cssselect('[itemprop="name"]')[0].text == 'Jochen Wegner'
    assert author.cssselect('[itemprop="url"]')[0].get('href') == (
        testserver.url + '/autoren/W/Jochen_Wegner/index')


def test_amp_shows_breaking_news_banner(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/amp?debug=eilmeldung')
    assert browser.cssselect('.breaking-news-banner')


def test_amp_has_correct_canonical_url(testbrowser, testserver):
    browser = testbrowser('/amp/zeit-online/article/amp')
    assert browser.cssselect('link[rel="canonical"]')[0].get('href') == (
        testserver.url + '/zeit-online/article/amp')
