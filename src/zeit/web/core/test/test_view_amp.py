# -*- coding: utf-8 -*-
import json
import lxml.etree
import urllib
import zeit.web.core.application


def test_amp_inline_svg_sprite_contains_no_xml_declaration(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/amp')
    sprite = browser.cssselect('.symbols')[0]
    assert '<?xml' not in lxml.etree.tostring(sprite)
    # redundant, but stresses what this test is all about
    assert '<?xml' not in browser.contents


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
    assert person.text == u'© Warner Bros./dpa'

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
    # check for assigned background-color class. selected randomly out of two.
    button_class = nextad.cssselect('.nextad__button')[0].get('class')
    assert button_class in ['nextad__button nextad__button--d11c08',
                            'nextad__button nextad__button--42661f']


def test_amp_shows_breaking_news_banner(testserver, httpbrowser):
    browser = httpbrowser('/amp/zeit-online/article/amp?debug=eilmeldung')
    assert len(browser.cssselect('.breaking-news-banner')) == 1


def test_amp_has_correct_canonical_url(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/amp')
    assert browser.cssselect('link[rel="canonical"]')[0].get('href') == (
        'http://localhost/zeit-online/article/amp')


def test_amp_article_has_valid_webtrekk_json(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/amp')
    json_source = browser.cssselect(
        'amp-analytics[type="webtrekk"] script'
    )[0].text

    try:
        webtrekk = json.loads(json_source)
        assert True
    except ValueError:
        assert False

    assert webtrekk['vars']['contentId'] == (
        "redaktion.wirtschaft...article.zede|localhost/zeit-online/article/amp"
    )

    page_vars = webtrekk['triggers']['trackPageview']['vars']
    assert page_vars['cp12'] == "mobile.site"
    assert page_vars['cp13'] == "amp"
    assert page_vars['cp25'] == "amp"


def test_amp_article_has_valid_webtrekk_click_json(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/amp')
    json_source = browser.cssselect(
        'amp-analytics[type="webtrekk"] script'
    )[0].text

    try:
        webtrekk = json.loads(json_source)
        assert True
    except ValueError:
        assert False

    assert 'trackLogoClick' in webtrekk['triggers']
    assert 'trackImprimtClick' in webtrekk['triggers']
    assert 'trackPrivacyClick' in webtrekk['triggers']
    assert 'trackTopClick' in webtrekk['triggers']
    assert 'trackBackToHomepageClick' in webtrekk['triggers']
    assert 'trackNextAdButtonClick' in webtrekk['triggers']
    assert 'trackNextAdImageClick' in webtrekk['triggers']
    assert 'trackFooterLogoClick' in webtrekk['triggers']
    assert 'trackFacebookClick' in webtrekk['triggers']
    assert 'trackTwitterClick' in webtrekk['triggers']
    assert 'trackWhatsAppClick' in webtrekk['triggers']
    assert 'trackMailClick' in webtrekk['triggers']
    assert 'trackAuthorClick' in webtrekk['triggers']
    assert 'trackNextReadClick' in webtrekk['triggers']
    assert 'trackKeywordsClick' in webtrekk['triggers']
    assert 'trackLocalInTextLinkClick' in webtrekk['triggers']
    assert 'trackExternInTextLinkClick' in webtrekk['triggers']


def test_amp_article_contains_sharing_links(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/amp')
    canonical = browser.cssselect('link[rel="canonical"]')[0].get('href')
    sharing = browser.cssselect('.article-sharing')[0]
    links = sharing.cssselect('.article-sharing__link')
    assert len(links) == 5
    assert ('?u=' + urllib.quote(canonical)) in links[0].get('href')
    assert ('url=' + urllib.quote(canonical)) in links[1].get('href')
    assert ('fb-messenger://share/?link=' + urllib.quote(canonical)
            ) in links[3].get('href')


def test_amp_article_shows_tags_correctly(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/amp')
    tags = browser.cssselect('.article-tags')[0]
    keywords = tags.cssselect('[itemprop="keywords"]')[0]
    assert tags.cssselect('.article-tags__title')[0].text == u'Schlagwörter'
    assert len(tags.cssselect('.article-tags__link')) == 5
    assert ' '.join(keywords.text_content().strip().split()) == (
        u'Flüchtling, Weltwirtschaftsforum Davos, '
        u'Arbeitsmarkt, Migration, Europäische Union')


def test_amp_article_shows_ads_correctly(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set('amp_advertising')
    browser = testbrowser('/amp/zeit-online/article/amp')
    ads = browser.cssselect('.advertising')
    assert len(ads) == 4


def test_amp_article_should_have_ivw_tracking(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set(
        'third_party_modules', 'tracking')
    browser = testbrowser('/amp/zeit-online/article/amp')
    ivw = browser.cssselect('amp-analytics[type="infonline"]')
    assert len(ivw) == 1
    ivw_text = lxml.etree.tostring(ivw[0])
    assert '"st":  "mobzeit"' in ivw_text
    assert '"cp":  "wirtschaft/bild-text"' in ivw_text
    assert '"url": "https://ssl.' in ivw_text
    assert 'static/latest/html/amp-analytics-infonline.html' in ivw_text


def test_amp_article_links_contain_tracking_data_attributes(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/amp')

    author = browser.cssselect('.byline a')[0]
    assert author.get('data-vars-url') == author.get('href').split('://')[1]

    tag = browser.cssselect('.article-tags__link')[1]
    assert tag.get('data-vars-url') == tag.get('href').split('://')[1]
    assert tag.get('data-vars-link-text') == 'Weltwirtschaftsforum Davos'
    assert tag.get('data-vars-number') == '2'


def test_amp_article_shows_volume_badge_for_subscription(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/zplus-zeit')
    volume_badge = browser.cssselect('.zplus-badge')[0]
    volume_text = volume_badge.cssselect('.zplus-badge__text')[0]

    assert volume_text.text.strip() == u'Exklusiv für Abonnenten'
    assert volume_badge.cssselect('.zplus-badge__icon')
    assert volume_badge.cssselect('.zplus-badge__media')


def test_amp_article_shows_volume_badge_for_registration(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/zplus-zeit-register')
    volume_badge = browser.cssselect('.zplus-badge')[0]
    volume_text = volume_badge.cssselect('.zplus-badge__text')[0]

    assert volume_text.text.strip() == u'Aus der ZEIT Nr. 49/2014'
    assert not volume_badge.cssselect('.zplus-badge__icon')
    assert volume_badge.cssselect('.zplus-badge__media')


def test_amp_article_shows_volume_badge_for_exclusive(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/zplus-zon')
    volume_badge = browser.cssselect('.zplus-badge')[0]
    volume_text = volume_badge.cssselect('.zplus-badge__text')[0]

    assert volume_text.text.strip() == u'Exklusiv für Abonnenten'
    assert volume_badge.cssselect('.zplus-badge__icon')


def test_amp_article_contains_authorbox(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/authorbox')
    authorbox = browser.cssselect('.authorbox')
    assert len(authorbox) == 3

    # test custom biography
    author = authorbox[0]
    description = author.cssselect('.authorbox__summary')[0]
    assert description.text.strip() == 'Text im Feld Kurzbio'
    assert description.get('itemprop') == 'description'

    # test author content and microdata
    author = authorbox[1]
    image = author.cssselect('[itemprop="image"]')[0]
    name = author.cssselect('strong[itemprop="name"]')[0]
    description = author.cssselect('[itemprop="description"]')[0]
    url = author.cssselect('a[itemprop="url"]')[0]

    assert author.get('itemtype') == 'http://schema.org/Person'
    assert author.get('itemscope') is not None
    assert ('http://localhost/autoren/W/Jochen_Wegner/jochen-wegner/square'
            ) in image.cssselect('[itemprop="url"]')[0].get('content')
    assert name.text.strip() == 'Jochen Wegner'
    assert description.text.strip() == 'Chefredakteur, ZEIT ONLINE.'
    assert url.get('href') == 'http://localhost/autoren/W/Jochen_Wegner/index'


def test_amp_article_shows_amp_accordion_for_infobox(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/infoboxartikel')
    infobox = browser.cssselect('.infobox')[0]
    accordion = infobox.cssselect('amp-accordion')[0]
    # required script
    assert browser.cssselect('script[custom-element="amp-accordion"]')
    # amp-accordion can contain one or more <section>s as its direct children
    assert len(infobox.cssselect('amp-accordion > section')) == 6
    assert len(infobox.cssselect('amp-accordion > *')) == 6
    # each <section> must contain exactly two direct children
    assert len(accordion.cssselect('section > *')) == 12
    # the first child (of the section) must be a heading
    assert len(accordion.cssselect('section > h3:first-child')) == 6
    # the second child (of the section) can be any tag allowed in AMP HTML
    assert len(accordion.cssselect('section > h3 + div')) == 6


def test_amp_article_has_placeholders_for_invalid_elements(testbrowser):
    browser = testbrowser('/amp/zeit-online/article/amp-invalid')
    json_source = browser.cssselect(
        'amp-analytics[type="webtrekk"] script'
    )[0].text

    select = testbrowser('/amp/zeit-online/article/amp-invalid').cssselect
    assert len(select('.article__placeholder')) == 4

    try:
        webtrekk = json.loads(json_source)
        assert True
    except ValueError:
        assert False

    page_vars = webtrekk['triggers']['trackPageview']['vars']
    assert page_vars['cp27'] == \
        "amp_platzhalter.2/seite-1;" \
        "amp_platzhalter.3/seite-1;" \
        "amp_platzhalter.4/seite-1;" \
        "amp_platzhalter.5/seite-1"
