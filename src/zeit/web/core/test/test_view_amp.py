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
        'filmstill-hobbit-schlacht-fuenf-hee/wide__820x461')
    assert image.cssselect('[itemprop="width"]')[0].get('content') == '820'
    assert image.cssselect('[itemprop="height"]')[0].get('content') == '461'
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


def test_amp_nextread_contains_required_microdata(testbrowser, testserver):
    browser = testbrowser('/amp/zeit-online/article/simple-nextread')

    article = browser.cssselect('article.nextread')[0]
    mainEntityOfPage = article.cssselect('[itemprop="mainEntityOfPage"]')[0]
    headline = article.cssselect('[itemprop="headline"]')[0]
    datePublished = article.cssselect('[itemprop="datePublished"]')[0]
    dateModified = article.cssselect('[itemprop="dateModified"]')[0]
    author = article.cssselect('[itemprop="author"]')[0]
    image = article.cssselect('[itemprop="image"]')[0]

    # check Article
    assert article.get('itemtype') == 'http://schema.org/Article'
    assert mainEntityOfPage.get('href') == (
        testserver.url + '/zeit-online/article/zeit')
    assert headline.text_content().strip() == (
        'Crystal Meth: Nancy braucht was Schnelles')
    assert datePublished.get('datetime') == '2015-02-12T04:32:17+01:00'
    assert dateModified.get('datetime') == '2015-02-15T18:18:50+01:00'
    assert author.get('itemtype') == 'http://schema.org/Person'
    assert author.cssselect('[itemprop="name"]')[0].text == 'Dorit Kowitz'
    assert author.cssselect('[itemprop="url"]')[0].get('href') == (
        testserver.url + '/autoren/K/Dorit_Kowitz')

    # check ImageObject
    assert image.get('itemtype') == 'http://schema.org/ImageObject'
    assert image.cssselect('[itemprop="url"]')[0].get('content') == (
        testserver.url + '/gesellschaft/2015-02/crystal-meth-nancy-schmidt/'
        'cinema__820x351')
    assert image.cssselect('[itemprop="width"]')[0].get('content') == '820'
    assert image.cssselect('[itemprop="height"]')[0].get('content') == '351'


def test_amp_shows_nextread_advertising(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/simple-verlagsnextread')
    nextad = browser.cssselect('aside.nextad')[0]
    assert nextad.cssselect('.nextad__label')[0].text == 'Verlagsangebot'
    assert len(nextad.cssselect('.nextad__title'))
    assert len(nextad.cssselect('.nextad__text'))
    # check for assigned background-color class
    assert nextad.cssselect('.nextad__button')[0].get('class') == (
        'nextad__button nextad__button--d11c08')


def test_amp_shows_breaking_news_banner(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/amp?debug=eilmeldung')
    assert browser.cssselect('.breaking-news-banner')


def test_amp_has_correct_canonical_url(testbrowser, testserver):
    browser = testbrowser('/amp/zeit-online/article/amp')
    assert browser.cssselect('link[rel="canonical"]')[0].get('href') == (
        testserver.url + '/zeit-online/article/amp')


def test_amp_article_has_correct_webtrekk_pixel(testbrowser, testserver):
    browser = testbrowser('/amp/zeit-online/article/amp')
    source = browser.cssselect('amp-pixel')[0].attrib.get('src')
    assert source == (
        u'//zeit01.webtrekk.net/981949533494636/wt.pl?p=328,'
        u'redaktion.wirtschaft...article.zede|{url}/zeit-online/article/amp'
        u',0,0,0,0,0,0,0,0&cg1=redaktion&cg2=article&cg3=wirtschaft&cg4=zede'
        u'&cg5=&cg6=&cg7=amp&cg8=wirtschaft/article&cg9=2016-01-22'
        u'&cp1=jochen wegner&cp2=wirtschaft/bild-text&cp3=1/2&cp4=wirtschaft;'
        u'flüchtlinge;flüchtling;weltwirtschaftsforum davos;arbeitsmarkt;'
        u'migration;europäische union&cp5=2016-01-22 11:55:46.556878+01:00'
        u'&cp6=7583&cp7=&cp8=zede&cp9=wirtschaft/article&cp10=&cp11='
        u'&cp12=mobile.site&cp13=mobile&cp15=&cp25=amp').format(
            url=testserver['http_address'])
