# -*- coding: utf-8 -*-
import lxml.etree

import zeit.web.core.application


def test_amp_paragraph_should_contain_expected_structure(tplbrowser):
    browser = tplbrowser('zeit.web.core:templates/amp/blocks/paragraph.html',
                         block=u'Wie lässt sich diese Floskel übersetzen? ')
    assert browser.cssselect('p.paragraph.article__item')
    assert browser.cssselect('p.paragraph.article__item')[0].text.strip() == (
        u'Wie lässt sich diese Floskel übersetzen?')


def test_amp_contains_required_microdata(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/amp')
    publisher = browser.cssselect('[itemprop="publisher"]')[0]
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

    # check Organization
    assert publisher.get('itemtype') == 'http://schema.org/Organization'
    assert publisher.cssselect('[itemprop="name"]')[0].get('content') == (
        'ZEIT ONLINE')
    assert publisher.cssselect('[itemprop="url"]')[0].get('href') == (
        'http://localhost/index')
    assert logo.get('itemtype') == 'http://schema.org/ImageObject'
    assert logo.cssselect('[itemprop="url"]')[0].get('content') == (
        'http://localhost/static/latest/images/'
        'structured-data-publisher-logo-zon.png')
    assert logo.cssselect('[itemprop="width"]')[0].get('content') == '565'
    assert logo.cssselect('[itemprop="height"]')[0].get('content') == '60'

    # check Article
    assert article.get('itemtype') == 'http://schema.org/Article'
    assert main_entity_of_page.get('content') == (
        'http://localhost/zeit-online/article/amp')
    text = headline.text_content().strip()
    assert text.startswith(u'Flüchtlinge: ')
    assert text.endswith(u'Mehr Davos, weniger Kreuth')
    assert len(description.text_content().strip())

    # check ImageObject
    assert image.get('itemtype') == 'http://schema.org/ImageObject'
    assert image.cssselect('[itemprop="url"]')[0].get('content') == (
        'http://localhost/zeit-online/image/'
        'filmstill-hobbit-schlacht-fuenf-hee/wide__820x461')
    assert image.cssselect('[itemprop="width"]')[0].get('content') == '820'
    assert image.cssselect('[itemprop="height"]')[0].get('content') == '461'
    assert len(image.cssselect('[itemprop="caption"]')) == 1
    assert copyright_holder.get('itemtype') == 'http://schema.org/Person'
    person = copyright_holder.cssselect('[itemprop="name"]')[0]
    assert person.text == u'© Warner Bros.'

    assert date_published.get('datetime') == '2016-01-22T11:55:46+01:00'
    assert date_modified.get('datetime') == '2016-01-22T11:55:46+01:00'

    assert author.get('itemtype') == 'http://schema.org/Person'
    assert author.cssselect('[itemprop="name"]')[0].text == 'Jochen Wegner'
    assert author.cssselect('[itemprop="url"]')[0].get('href') == (
        'http://localhost/autoren/W/Jochen_Wegner/index')


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


def test_amp_has_correct_canonical_url(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/amp')
    assert browser.cssselect('link[rel="canonical"]')[0].get('href') == (
        'http://localhost/zeit-online/article/amp')


def test_amp_article_has_correct_webtrekk_pixel(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/amp')
    source = browser.cssselect('amp-pixel')[0].attrib.get('src')
    assert source == (
        u'https://zeit01.webtrekk.net/981949533494636/wt.pl?p=328,'
        u'redaktion.wirtschaft...article.zede%7C'
        u'localhost/zeit-online/article/amp'
        u',0,0,0,0,0,0,0,0&cg1=redaktion&cg2=article&cg3=wirtschaft&cg4=zede'
        u'&cg5=&cg6=&cg7=amp&cg8=wirtschaft/article&cg9=2016-01-22'
        u'&cp1=jochen wegner&cp2=wirtschaft/bild-text&cp3=1/2&cp4=wirtschaft;'
        u'flüchtlinge;flüchtling;weltwirtschaftsforum davos;arbeitsmarkt;'
        u'migration;europäische union&cp5=2016-01-22 11:55:46.556878+01:00'
        u'&cp6=7583&cp7=&cp8=zede&cp9=wirtschaft/article&cp10=&cp11='
        u'&cp12=mobile.site&cp13=mobile&cp15=&cp25=amp')


def test_amp_article_contains_sharing_links(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/amp')
    canonical = browser.cssselect('link[rel="canonical"]')[0].get('href')
    sharing = browser.cssselect('.article-sharing')[0]
    links = sharing.cssselect('.article-sharing__link')
    assert sharing.cssselect('.article-sharing__title')[0].text == 'Teilen'
    assert len(links) == 4
    assert ('?u=' + canonical) in links[0].get('href')
    assert ('url=' + canonical) in links[1].get('href')


def test_amp_article_shows_tags_correctly(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/amp')
    tags = browser.cssselect('.article-tags')[0]
    keywords = tags.cssselect('[itemprop="keywords"]')[0]
    assert tags.cssselect('.article-tags__title')[0].text == 'Schlagworte'
    assert len(tags.cssselect('.article-tags__link')) == 5
    assert ' '.join(keywords.text_content().strip().split()) == (
        u'Flüchtling, Weltwirtschaftsforum Davos, '
        u'Arbeitsmarkt, Migration, Europäische Union')


def test_amp_article_shows_ads_correctly(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/amp')
    ads = browser.cssselect('.advertising')
    assert len(ads) == 3


def test_amp_article_should_have_ivw_tracking(testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'third_party_modules': True, 'tracking': True}.get)
    browser = testbrowser('/amp/zeit-online/article/amp')
    ivw = browser.cssselect('amp-analytics[type="infonline"]')
    assert len(ivw) == 1
    ivw_text = lxml.etree.tostring(ivw[0])
    assert '"st":  "mobzeit"' in ivw_text
    assert '"cp":  "wirtschaft/bild-text"' in ivw_text
    assert '"url": "https://ssl.' in ivw_text
    assert 'static/latest/html/amp-analytics-infonline.html' in ivw_text
