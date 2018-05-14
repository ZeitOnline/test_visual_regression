# -*- coding: utf-8 -*-
import base64
import datetime
import urlparse

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
import lxml.etree
import mock
import pyramid.testing
import pytest
import requests
import zope.component

from zeit.cms.checkout.helper import checked_out
import zeit.cms.related.interfaces
import zeit.cms.interfaces
import zeit.content.image.interfaces

import zeit.solr.interfaces

import zeit.web.core.application
import zeit.web.site.view_article


screen_sizes = ((320, 480, True), (520, 960, True),
                (768, 1024, False), (1000, 1024, False))


@pytest.fixture(scope='session', params=screen_sizes)
def screen_size(request):
    return request.param


def test_article_should_render_full_view(testbrowser):
    browser = testbrowser('/zeit-online/article/zeit/komplettansicht')
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/zeit')
    assert len(browser.cssselect(
        '.article-page > p.paragraph')) == article.paragraphs


def test_article_single_page_has_no_pagination(testbrowser):
    select = testbrowser('/zeit-online/article/simple').cssselect

    assert len(select('.summary, .byline, .metadata')) == 3
    assert len(select('.article-pagination')) == 1
    assert len(select('.article-pager')) == 0
    assert len(select('.article-toc')) == 0


def test_article_full_view_has_no_pagination(testbrowser):
    select = testbrowser('/zeit-online/article/zeit/komplettansicht').cssselect

    assert len(select('.summary, .byline, .metadata')) == 3
    assert len(select('.article-pagination')) == 1
    assert len(select('.article-pager')) == 0
    assert len(select('.article-toc')) == 0


def test_article_types_have_back_to_home_button(testbrowser):
    select = testbrowser('/zeit-online/article/zeit/komplettansicht').cssselect
    button = select('.article-pagination .article-pagination__button')
    assert button[0].text == 'Startseite'
    select = testbrowser('/zeit-online/article/simple').cssselect
    button = select('.article-pagination .article-pagination__button')
    assert button[0].text == 'Startseite'
    select = testbrowser('/zeit-online/article/zeit/seite-5').cssselect
    button = select('.article-pagination .article-pagination__button')
    assert button[0].text == 'Startseite'

    # test link
    link = select('.article-pagination__link')[0].get('href')
    assert '/index' in link


def test_article_pagination(testbrowser):
    select = testbrowser('/zeit-online/article/zeit').cssselect
    nexttitle = select('.article-pagination__nexttitle')
    numbers = select('.article-pager__number')

    assert len(select('.summary, .byline, .metadata')) == 3
    assert len(select('.article__page-teaser')) == 0
    assert len(select('.article-pagination')) == 1
    assert len(nexttitle) == 1
    assert nexttitle[0].text.strip() == (
        u'Der Horror von Crystal wurzelt in der Normalität')
    assert len(numbers) == 5
    assert '--current' in numbers[0].get('class')
    assert len(select('.article-toc')) == 1
    assert len(select('.article-toc__item')) == 5
    assert '--current' in select('.article-toc__item')[0].get('class')


def test_article_paginator_has_https_links(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.unset('https')
    select = testbrowser('/zeit-online/article/zeit').cssselect
    pages = select('.article-pager__number a')
    assert 'https://' not in pages[0].attrib.get('href')

    zeit.web.core.application.FEATURE_TOGGLES.set('https')
    select = testbrowser('/zeit-online/article/zeit').cssselect
    pages = select('.article-pager__number a')
    assert 'https://' in pages[0].attrib.get('href')


def test_article_pagination_active_state(testbrowser):
    select = testbrowser('/zeit-online/article/zeit/seite-3').cssselect

    assert len(select('.summary, .byline, .metadata')) == 0
    assert select('.article__page-teaser')[0].text.strip() == (
        u'Seite 3/5:')
    assert select('.article__page-teaser > h1')[0].text.strip() == (
        u'Man wird schlank und lüstern')
    assert select('.article-pagination__nexttitle')[0].text.strip() == (
        u'Aus dem abenteuerlustigen Mädchen vom Dorf wurde ein Junkie')
    assert '--current' in select('.article-pager__number')[2].get('class')
    assert len(select('.article-toc')) == 1
    assert len(select('.article-toc__item')) == 5
    assert '--current' in select('.article-toc__item')[2].get('class')


def test_article_toc_has_mobile_functionality(testserver, selenium_driver):

    selenium_driver.set_window_size(320, 480)
    selenium_driver.get('{}/zeit-online/article/zeit'.format(testserver.url))

    toc_box = selenium_driver.find_element_by_css_selector('.article-toc')
    toc_button = toc_box.find_element_by_css_selector('.article-toc__headline')
    toc_onesie = toc_box.find_element_by_css_selector('.article-toc__onesie')
    toc_list = toc_box.find_element_by_css_selector('.article-toc__list')

    # before click
    condition = expected_conditions.invisibility_of_element_located((
        By.CSS_SELECTOR, '.article-toc__list'))
    assert WebDriverWait(
        selenium_driver, 1).until(condition)
    assert toc_button.get_attribute('role') == 'button'
    assert toc_list.get_attribute('role') == 'region'
    assert toc_button.get_attribute('aria-expanded') == 'false'
    assert toc_list.get_attribute('aria-hidden') == 'true'

    # after click
    toc_button.click()
    condition = expected_conditions.visibility_of_element_located((
        By.CSS_SELECTOR, '.article-toc__list'))
    assert WebDriverWait(
        selenium_driver, 1).until(condition)
    assert toc_button.get_attribute('aria-expanded') == 'true'
    assert toc_list.get_attribute('aria-hidden') == 'false'

    # after second click
    toc_button.click()
    condition = expected_conditions.invisibility_of_element_located((
        By.CSS_SELECTOR, '.article-toc__list'))
    assert WebDriverWait(
        selenium_driver, 1).until(condition)
    assert toc_button.get_attribute('aria-expanded') == 'false'
    assert toc_list.get_attribute('aria-hidden') == 'true'

    # click on onesie
    toc_onesie.click()
    assert '/komplettansicht' in selenium_driver.current_url


def test_article_page_1_has_correct_h1(testbrowser):
    select = testbrowser('/zeit-online/article/zeit').cssselect
    node = '.article__item > h1 > .article-heading__title'
    assert select(node)[0].text.strip() == (
        u'Nancy braucht was Schnelles'), (
            'article headline is not h1')


def test_article_page_2_has_correct_h1(testbrowser):
    select = testbrowser('/zeit-online/article/zeit/seite-2').cssselect
    node = '.article__page-teaser > h1'
    assert select(node)[0].text.strip() == (
        u'Der Horror von Crystal wurzelt in der Normalität'), (
            'article page teaser is not h1')


def test_article_page_teaserless_has_correct_h1(testbrowser):
    select = testbrowser('/zeit-online/article/zeit/seite-5').cssselect
    node = '.article__item > h1 > .article-heading__title'
    assert select(node)[0].text.strip() == (
        u'Nancy braucht was Schnelles'), (
            'article headline is not h1')


def test_article_complete_has_correct_h1(testbrowser):
    select = testbrowser('/zeit-online/article/zeit/komplettansicht').cssselect
    node = '.article__item > h1 > .article-heading__title'
    assert select(node)[0].text.strip() == (
        u'Nancy braucht was Schnelles'), (
            'article headline is not h1')


def test_article_plain_has_correct_h1(testbrowser):
    select = testbrowser('/zeit-online/article/simple').cssselect
    node = '.article__item > h1 > .article-heading__title'
    assert select(node)[0].text.strip() == (
        u'Williams wackelt weiter, steht aber im Viertelfinale'), (
            'article headline must be h1')


def test_article_page_1_has_correct_title(testbrowser):
    select = testbrowser('/zeit-online/article/zeit').cssselect
    assert select('title')[0].text.strip() == (
        u'Crystal Meth: Nancy braucht was Schnelles |\xa0ZEIT ONLINE'), (
            'article headline is not title')


def test_article_page_2_has_correct_title(testbrowser):
    select = testbrowser('/zeit-online/article/zeit/seite-2').cssselect
    assert select('title')[0].text.strip() == (
        u'Crystal Meth: Der Horror von Crystal '
        u'wurzelt in der Normalität |\xa0ZEIT ONLINE'), (
            'article page teaser is not title')


def test_article_page_teaserless_has_correct_title(testbrowser):
    select = testbrowser('/zeit-online/article/zeit/seite-5').cssselect
    assert select('title')[0].text.strip() == (
        u'Crystal Meth: Nancy braucht was Schnelles |\xa0ZEIT ONLINE'), (
            'article headline is not title')


def test_article_complete_has_correct_title(testbrowser):
    select = testbrowser('/zeit-online/article/zeit/komplettansicht').cssselect
    assert select('title')[0].text.strip() == (
        u'Crystal Meth: Nancy braucht was Schnelles |\xa0ZEIT ONLINE'), (
            'article headline is not title')


def test_article_plain_has_correct_title(testbrowser):
    select = testbrowser('zeit-online/article/02').cssselect
    assert select('title')[0].text.strip() == (
        u'Zwei Baguettes und ein Zimmer bitte |\xa0ZEIT ONLINE'), (
            'article headline is not title')


def test_fresh_breaking_news_article_renders_breaking_bar(testbrowser):
    browser = testbrowser('/zeit-online/article/eilmeldungsartikel')

    assert len(browser.cssselect('.breaking-news-banner')) == 1
    assert len(browser.cssselect('.breaking-news-heading')) == 1


def test_stale_breaking_news_article_must_not_render_breaking_bar(testbrowser):
    browser = testbrowser('/zeit-online/article/alte-eilmeldung')

    assert len(browser.cssselect('.breaking-news-banner')) == 0
    assert len(browser.cssselect('.breaking-news-heading')) == 0


def test_schema_org_main_content_of_page(testbrowser):
    select = testbrowser('/zeit-online/article/01').cssselect

    assert len(select('main[itemprop="mainContentOfPage"]')) == 1


def test_schema_org_article_mark_up(testbrowser):
    browser = testbrowser('/zeit-online/article/01')
    publisher = browser.cssselect('[itemprop="publisher"]')[0]
    logo = publisher.cssselect('[itemprop="logo"]')[0]

    article = browser.cssselect('article[itemprop="mainEntity"]')[0]
    main_entity_of_page = article.cssselect('[itemprop="mainEntityOfPage"]')[0]
    headline = article.cssselect('[itemprop="headline"]')[0]
    description = article.cssselect('[itemprop="description"]')[0]
    date_published = article.cssselect('[itemprop="datePublished"]')[0]
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
    assert main_entity_of_page.get('href') == (
        'http://localhost/zeit-online/article/01')
    assert ' '.join(headline.text_content().strip().split()) == (
        u'"Der Hobbit": Geht\'s noch gr\xf6\xdfer?')

    assert len(description.text_content().strip())
    assert len(article.cssselect('[itemprop="articleBody"]')) == 1

    # check ImageObject
    assert image.get('itemtype') == 'http://schema.org/ImageObject'
    assert len(image.cssselect('[itemprop="caption"]')) == 1
    assert copyright_holder.get('itemtype') == 'http://schema.org/Person'
    person = copyright_holder.cssselect('[itemprop="name"]')[0]
    assert person.text == u'© Warner Bros./dpa'

    assert date_published.get('datetime') == '2015-05-27T19:11:30+02:00'

    assert author.get('itemtype') == 'http://schema.org/Person'
    assert author.cssselect('[itemprop="name"]')[0].text == 'Wenke Husmann'
    assert author.cssselect('[itemprop="url"]')[0].get('href') == (
        'http://localhost/autoren/H/Wenke_Husmann/index.xml')


def test_multipage_article_should_designate_meta_pagination(testbrowser):
    browser = testbrowser('/zeit-online/article/zeit')
    assert not browser.xpath('//head/link[@rel="prev"]')
    href = browser.xpath('//head/link[@rel="next"]')[0].get('href')
    assert href.endswith('zeit-online/article/zeit/seite-2')

    browser = testbrowser('/zeit-online/article/zeit/seite-2')
    href = browser.xpath('//head/link[@rel="prev"]')[0].get('href')
    assert href.endswith('zeit-online/article/zeit')
    href = browser.xpath('//head/link[@rel="next"]')[0].get('href')
    assert href.endswith('zeit-online/article/zeit/seite-3')

    browser = testbrowser('/zeit-online/article/zeit/seite-5')
    href = browser.xpath('//head/link[@rel="prev"]')[0].get('href')
    assert href.endswith('zeit-online/article/zeit/seite-4')
    assert not browser.xpath('//head/link[@rel="next"]')


def test_other_page_types_should_not_designate_meta_pagination(testbrowser):
    browser = testbrowser('/zeit-online/article/01')
    assert not browser.xpath('//head/link[@rel="prev"]')
    assert not browser.xpath('//head/link[@rel="next"]')

    browser = testbrowser('/zeit-online/index')
    assert not browser.xpath('//head/link[@rel="prev"]')
    assert not browser.xpath('//head/link[@rel="next"]')


def test_article_obfuscated_source_with_date_print_published(dummy_request):
    content = mock.Mock()
    content.product.label = content.product.title = 'DIE ZEIT'
    content.product.show = 'issue'
    content.copyrights = ''
    content.volume = 1
    content.year = 2011
    view = zeit.web.site.view_article.Article(content, dummy_request)
    view.date_print_published = datetime.datetime(2011, 1, 6)
    source = u'DIE ZEIT Nr.\u00A01/2011, 6. Januar 2011'
    assert view.source_label == u'DIE ZEIT Nr.\u00A01/2011'
    assert view.obfuscated_source == base64.b64encode(source.encode('latin-1'))
    assert view.unobfuscated_source == source


def test_article_obfuscated_source_without_date_print_published(dummy_request):
    content = mock.Mock()
    content.product.label = content.product.title = 'DIE ZEIT'
    content.product.show = 'issue'
    content.copyrights = ''
    content.volume = 1
    content.year = 2011
    view = zeit.web.site.view_article.Article(content, dummy_request)
    view.date_print_published = None
    assert view.source_label == u'DIE ZEIT Nr.\u00A01/2011'
    assert not view.obfuscated_source
    assert not view.unobfuscated_source


def test_article_sharing_menu_should_hide_app_links_tablet_upwards(
        testserver, selenium_driver):
    selenium_driver.set_window_size(768, 800)
    selenium_driver.get('{}/zeit-online/article/01'.format(testserver.url))

    whatsapp_item = selenium_driver.find_element_by_css_selector(
        '.sharing-menu__item--whatsapp')
    messenger_item = selenium_driver.find_element_by_css_selector(
        '.sharing-menu__item--messenger')

    assert not whatsapp_item.is_displayed(), (
        'Sharing link to WhatsApp should be hidden on tablet & desktop')
    assert not messenger_item.is_displayed(), (
        'Sharing link for Facebook Messenger '
        'must be invisible on tablet & desktop')


def test_article_sharing_links_should_be_url_encoded(testbrowser):
    browser = testbrowser('/zeit-online/article/01')
    # it's hard to check for url-encodedness,
    # but checking for unencoded spaces nearly should do the trick
    spacey_sharing_links = browser.cssselect(
        '.sharing-menu .sharing-menu__link[href*=" "]')
    assert len(spacey_sharing_links) == 0


def test_article_tags_are_present_and_limited(testbrowser):
    browser = testbrowser('/zeit-online/article/tags')
    tags = browser.cssselect('.article-tags')
    links = tags[0].find_class('article-tags__link')

    assert len(tags) == 1
    assert len(tags[0].find_class('article-tags__title')) == 1
    assert len(links) == 6
    for link in links:
        assert link.get('rel') == 'tag'


def test_infobox_in_article_is_shown(testbrowser):
    select = testbrowser('/zeit-online/article/infoboxartikel').cssselect
    assert len(select('aside#info-bonobo.infobox')) == 1
    assert len(select('#info-bonobo .infobox-tab__title')) == 6


def test_infobox_mobile_actions(testserver, selenium_driver, screen_size):
    selenium_driver.set_window_size(screen_size[0], screen_size[1])
    selenium_driver.get('{}/zeit-online/article/infoboxartikel'.format(
        testserver.url))
    infobox = selenium_driver.find_element_by_id('info-bonobo')
    tabnavigation = infobox.find_elements_by_class_name('infobox__navigation')
    tabpanels = infobox.find_elements_by_class_name('infobox-tab__panel')
    clicker = infobox.find_elements_by_css_selector(
        '.infobox-tab .infobox-tab__link')

    assert infobox.is_displayed(), 'Infobox missing'

    if screen_size[0] == 320 or screen_size[0] == 520:
        assert not tabnavigation[0].is_displayed(), 'Mobile not accordion'
        assert tabpanels[0].get_attribute('aria-hidden') == 'true'
        assert tabpanels[1].get_attribute('aria-hidden') == 'true'
        assert tabpanels[2].get_attribute('aria-hidden') == 'true'
        assert tabpanels[3].get_attribute('aria-hidden') == 'true'
        assert tabpanels[4].get_attribute('aria-hidden') == 'true'
        assert tabpanels[5].get_attribute('aria-hidden') == 'true'
        clicker[0].click()
        assert tabpanels[0].get_attribute('aria-hidden') == 'false'
        clicker[1].click()
        assert tabpanels[1].get_attribute('aria-hidden') == 'false'
        clicker[3].click()
        assert tabpanels[3].get_attribute('aria-hidden') == 'false'
        clicker[5].click()
        assert tabpanels[5].get_attribute('aria-hidden') == 'false'
        clicker[0].click()
        assert tabpanels[0].get_attribute('aria-hidden') == 'true'


def test_infobox_desktop_actions(testserver, selenium_driver, screen_size):
    selenium_driver.set_window_size(screen_size[0], screen_size[1])
    selenium_driver.get('{}/zeit-online/article/infoboxartikel'.format(
        testserver.url))
    infobox = selenium_driver.find_element_by_id('info-bonobo')
    tabnavigation = infobox.find_elements_by_class_name(
        'infobox__navigation')[0]
    tabpanels = infobox.find_elements_by_class_name('infobox-tab__panel')
    clicker = infobox.find_elements_by_css_selector(
        '.infobox__navigation .infobox-tab__link')

    assert infobox.is_displayed(), 'Infobox missing'

    if screen_size[0] > 767:
        assert tabnavigation.is_displayed(), 'Desktop not Tabs'
        assert tabpanels[0].get_attribute('aria-hidden') == 'false'
        assert tabpanels[1].get_attribute('aria-hidden') == 'true'
        assert tabpanels[2].get_attribute('aria-hidden') == 'true'
        assert tabpanels[3].get_attribute('aria-hidden') == 'true'
        assert tabpanels[4].get_attribute('aria-hidden') == 'true'
        assert tabpanels[5].get_attribute('aria-hidden') == 'true'
        clicker[0].click()
        assert tabpanels[0].get_attribute('aria-hidden') == 'false'
        clicker[1].click()
        assert tabpanels[0].get_attribute('aria-hidden') == 'true'
        assert tabpanels[1].get_attribute('aria-hidden') == 'false'
        clicker[3].click()
        assert tabpanels[0].get_attribute('aria-hidden') == 'true'
        assert tabpanels[1].get_attribute('aria-hidden') == 'true'
        assert tabpanels[2].get_attribute('aria-hidden') == 'true'
        assert tabpanels[3].get_attribute('aria-hidden') == 'false'


def test_article_has_news_source_as_list():
    content = mock.Mock()
    content.copyrights = 'ZEIT ONLINE, Reuters'

    view = zeit.web.site.view_article.Article(
        content, pyramid.testing.DummyRequest())
    assert view.news_source == 'ZEITONLINE;Reuters'


def test_article_has_news_source_dpa():
    content = mock.Mock()
    content.ressort = 'News'
    content.product.id = 'News'
    view = zeit.web.site.view_article.Article(
        content, pyramid.testing.DummyRequest())
    assert view.news_source == "dpa"


def test_article_has_news_source_sid():
    content = mock.Mock()
    content.product.id = 'SID'
    view = zeit.web.site.view_article.Article(
        content, pyramid.testing.DummyRequest())
    assert view.news_source == "Sport-Informations-Dienst"


def test_article_has_news_source_empty():
    content = mock.Mock()
    content.copyrights = None

    view = zeit.web.site.view_article.Article(
        content, pyramid.testing.DummyRequest())
    assert view.news_source == ''


def test_article_news_source_should_not_break_without_product():
    # While product is required in vivi, we've seen content without one
    # in production preview (presumably while the article is being created).
    content = mock.Mock()
    content.copyrights = None
    content.ressort = 'News'
    content.product = None

    view = zeit.web.site.view_article.Article(
        content, pyramid.testing.DummyRequest())
    assert view.news_source == ''


def test_article_view_renders_alldevices_raw_box(testbrowser):
    browser = testbrowser('/zeit-online/article/raw-box')
    assert 'fVwQok9xnLGOA' in browser.contents


def test_article_skips_raw_box_not_suitable_for_alldevices(testbrowser):
    browser = testbrowser('/zeit-online/article/raw-box')
    assert 'cYhaIIyjjxg1W' not in browser.contents


def test_nextread_is_placed_on_article(testbrowser):
    browser = testbrowser('/zeit-online/article/simple-nextread')
    assert len(browser.cssselect('#nextread')) == 1


def test_nextread_date_looks_less_like_a_date_for_google(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/article/nextread.tpl')
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/simple-nextread')
    request = pyramid.testing.DummyRequest(
        route_url=lambda x: 'http://foo.bar/',
        asset_host='',
        image_host='')
    view = zeit.web.site.view_article.Article(content, request)
    html_str = tpl.render(view=view, module=view.nextread, request=request)
    html = lxml.html.fromstring(html_str)
    datetime = html.cssselect('.nextread__dt')
    assert datetime[0].tag == 'span'
    assert not any(x in datetime[0].get('class') for x in ['date', 'time'])


def test_nextread_is_responsive(testserver, selenium_driver, screen_size):
    url = '{}/zeit-online/article/simple-nextread'.format(testserver.url)
    selenium_driver.set_window_size(screen_size[0], screen_size[1])
    selenium_driver.get(url)
    nextread = selenium_driver.find_element_by_id('nextread')

    assert nextread.is_displayed(), 'Nextread missing'

    if screen_size[0] == 320:
        assert nextread.size.get('height') > 137

    if screen_size[0] == 520:
        assert nextread.size.get('height') > 220

    if screen_size[0] == 768:
        assert nextread.size.get('height') < 350

    if screen_size[0] == 1000:
        assert nextread.size.get('height') < 450


def test_publisher_nextread_on_article_has_own_template(testbrowser):
    browser = testbrowser('/zeit-online/article/simple-verlagsnextread')
    assert len(browser.cssselect('.nextread-advertisement')) == 1


def test_zon_nextread_teaser_block_has_teasers_available(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/simple-nextread')
    nextread = zeit.web.core.interfaces.INextread(context)
    assert hasattr(nextread, '__iter__')
    assert len(nextread) == 1
    assert nextread[0].uniqueId.endswith('/zeit-online/article/zeit')


def test_article_column_should_have_no_body_image(testbrowser):
    browser = testbrowser('/zeit-online/cp-content/kolumne')
    assert not browser.cssselect('.article-body img')


def test_article_column_author_image_should_be_present(testbrowser):
    browser = testbrowser('/zeit-online/cp-content/kolumne')
    img = browser.cssselect(
        '.column-heading__author .column-heading__media-item')
    ratio = img[0].get('data-ratio')
    src = img[0].get('src')
    assert src != "" and ratio != ""


def test_article_should_not_break_on_author_without_image(
        testbrowser, workingcopy):
    author = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/autoren/author3')
    with checked_out(author) as co:
        zeit.content.image.interfaces.IImages(co).image = None
    browser = testbrowser('/zeit-online/cp-content/kolumne')
    assert not browser.cssselect(
        '.column-heading__author .column-heading__media-item')


def test_article_should_not_break_without_author(
        testbrowser, workingcopy):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/cp-content/kolumne')
    with checked_out(content) as co:
        co.authorships = ()
    browser = testbrowser('/zeit-online/cp-content/kolumne')
    assert not browser.cssselect(
        '.column-heading__author .column-heading__media-item')


def test_article_column_without_authorimage_should_be_same(testbrowser):
    browser = testbrowser('/zeit-online/cp-content/kolumne-ohne-autorenbild')
    assert len(browser.cssselect('.article--columnarticle')) == 1
    assert len(browser.cssselect('.column-heading')) == 1


def test_article_column_should_be_identifiable_by_suitable_css_class(
        testbrowser):
    browser = testbrowser('/zeit-online/cp-content/kolumne')
    assert browser.cssselect('.article.article--columnarticle')
    assert browser.cssselect('.article-body.article-body--columnarticle')


def test_article_column_pages_should_render_correctly(testbrowser):
    browser = testbrowser('/zeit-online/article/fischer/seite-2')
    assert browser.cssselect('.column-heading__upper')
    assert len(browser.cssselect('.column-heading__lower')) == 0
    assert browser.cssselect('.article__page-teaser--column')


def test_article_should_show_main_image_from_imagegroup(testbrowser):
    browser = testbrowser('/zeit-online/article/01')
    images = browser.cssselect('.article__item img')
    assert 'filmstill-hobbit-schlacht-fuenf-hee' in images[0].get('src')


def test_article_should_have_proper_meetrics_integration(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set('third_party_modules')
    browser = testbrowser('/zeit-online/article/01')
    meetrics = browser.cssselect(
        'script[src="//s62.mxcdn.net/bb-serve/mtrcs_225560.js"]')
    assert len(meetrics) == 1


def test_breaking_news_article_shows_date_first_released(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/article_breaking.html')
    view = mock.Mock()
    view.date_first_released = datetime.time(11, 55, 0)
    lines = tpl.blocks['breaking_news'](tpl.new_context({'view': view}))
    html_str = ' '.join(lines).strip()
    html = lxml.html.fromstring(html_str)
    time = html.cssselect('.breaking-news-banner__time')
    assert time[0].text == '11:55 Uhr'


def test_does_not_break_when_author_has_no_display_name(testbrowser):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/08')
    article_view = zeit.web.magazin.view_article.Article(
        context, pyramid.testing.DummyRequest())
    with mock.patch('zeit.content.author.author.Author.display_name', None):
        assert article_view.authors_list == ''


def test_article_views_have_page_numbers_in_data_attribute(testbrowser):
    select_fullview = testbrowser(
        '/zeit-online/article/zeit/komplettansicht').cssselect
    assert len(select_fullview('.article-page[data-page-number="1"]')) == 1
    assert len(select_fullview('.article-page[data-page-number="2"]')) == 1
    assert len(select_fullview('.article-page[data-page-number="3"]')) == 1
    assert len(select_fullview('.article-page[data-page-number="4"]')) == 1
    assert len(select_fullview('.article-page[data-page-number="5"]')) == 1

    select_firstpage = testbrowser(
        '/zeit-online/article/zeit').cssselect
    assert len(select_firstpage('.article-page[data-page-number="1"]')) == 1
    assert len(select_firstpage('.article-page[data-page-number="2"]')) == 0

    select_page3 = testbrowser(
        '/zeit-online/article/zeit/seite-3').cssselect
    assert len(select_page3('.article-page[data-page-number="1"]')) == 0
    assert len(select_page3('.article-page[data-page-number="3"]')) == 1


def test_messy_archive_metadata_should_have_minimal_breadcrumbs(
        application, monkeypatch):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    monkeypatch.setattr(
        zeit.web.site.view_article.Article, u'product_id', u'ZEI')
    monkeypatch.setattr(
        zeit.content.article.article.Article, u'year', None)
    monkeypatch.setattr(
        zeit.content.article.article.Article, u'volume', u'xx')
    article_view = zeit.web.site.view_article.Article(
        context, pyramid.testing.DummyRequest())
    # Fallback to default breadcrumbs, including the article title
    assert article_view.title in article_view.breadcrumbs[1][0]


def test_old_archive_text_without_divisions_should_render_paragraphs(
        testbrowser):
    browser = testbrowser('/zeit-online/article/alter-archivtext')
    assert len(browser.cssselect('.article__item.paragraph')) == 7
    assert len(browser.cssselect('.article-pager__number')) == 3


def test_zear_article_has_correct_meta_robots(
        application, monkeypatch, dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    monkeypatch.setattr(
        zeit.web.site.view_article.Article, u'product_id', u'ZEAR')
    monkeypatch.setattr(
        zeit.web.site.view_article.Article, u'ressort', u'Fehler')
    view = zeit.web.site.view_article.Article(context, dummy_request)
    assert view.meta_robots == 'noindex,follow,noarchive'


def test_tgs_article_has_correct_meta_robots(
        application, monkeypatch, dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    monkeypatch.setattr(
        zeit.web.site.view_article.Article, u'product_id', u'TGS')
    view = zeit.web.site.view_article.Article(context, dummy_request)
    assert view.meta_robots == 'noindex,follow,noarchive'


def test_habl_article_has_correct_meta_robots(
        application, monkeypatch, dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    monkeypatch.setattr(
        zeit.web.site.view_article.Article, u'product_id', u'HaBl')
    view = zeit.web.site.view_article.Article(context, dummy_request)
    assert view.meta_robots == 'noindex,follow,noarchive'


def test_wiwo_article_has_correct_meta_robots(
        application, monkeypatch, dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    monkeypatch.setattr(
        zeit.web.site.view_article.Article, u'product_id', u'WIWO')
    view = zeit.web.site.view_article.Article(context, dummy_request)
    assert view.meta_robots == 'noindex,follow,noarchive'


def test_golem_article_has_correct_meta_robots(
        application, monkeypatch, dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    monkeypatch.setattr(
        zeit.web.site.view_article.Article, u'product_id', u'GOLEM')
    view = zeit.web.site.view_article.Article(context, dummy_request)
    assert view.meta_robots == 'noindex,follow,noarchive'


def test_sharing_cardstack_article_has_correct_meta_robots(
        application, monkeypatch, dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    monkeypatch.setattr(
        zeit.web.site.view_article.Article, u'shared_cardstack_id', u'kekse')
    view = zeit.web.site.view_article.Article(context, dummy_request)
    assert view.meta_robots == 'noindex,follow,noarchive'


def test_zei_article_has_correct_meta_robots(
        application, monkeypatch, dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    monkeypatch.setattr(
        zeit.web.site.view_article.Article, u'product_id', u'ZEI')
    view = zeit.web.site.view_article.Article(context, dummy_request)
    assert view.meta_robots == 'index,follow,noarchive'


def test_unset_product_id_article_has_correct_meta_robots(
        application, monkeypatch, dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    monkeypatch.setattr(
        zeit.web.site.view_article.Article, u'product_id', None)
    view = zeit.web.site.view_article.Article(context, dummy_request)
    assert view.meta_robots == 'index,follow,noarchive'


def test_article_has_correct_meta_keywords(
        application, monkeypatch, dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')

    # all values
    monkeypatch.setattr(
        zeit.web.site.view_article.Article, u'ressort', u'politik')
    monkeypatch.setattr(
        zeit.web.site.view_article.Article, u'supertitle', u'Der Supertitle')
    monkeypatch.setattr(
        zeit.web.core.view.Base, u'meta_keywords', [u'foo', u'bar'])
    article = zeit.web.site.view_article.Article(context, dummy_request)
    assert article.meta_keywords == [
        'Politik', 'Der Supertitle', 'foo', 'bar']

    # missing values
    monkeypatch.setattr(
        zeit.web.site.view_article.Article, u'ressort', u'')
    monkeypatch.setattr(
        zeit.web.site.view_article.Article, u'supertitle', u'Der Supertitle')
    monkeypatch.setattr(
        zeit.web.core.view.Base, u'meta_keywords', [])
    article_view = zeit.web.site.view_article.Article(context, dummy_request)
    assert article_view.meta_keywords == ['Der Supertitle']


def test_robots_rules_for_angebote_articles(application):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    request = pyramid.testing.DummyRequest()

    # usual angebot
    request.path = '/angebote/buchtipp/ishiguro/index'
    view = zeit.web.site.view_article.Article(article, request)
    assert view.meta_robots == 'index,nofollow,noarchive', (
        'wrong robots for usual angebot')

    # partnersuche
    request.path = '/angebote/partnersuche/test'
    view = zeit.web.site.view_article.Article(article, request)
    assert view.meta_robots == 'index,follow,noarchive', (
        'wrong robots for partnersuche')


def test_robots_rules_for_diverse_articles(application):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    request = pyramid.testing.DummyRequest()
    request.url = 'http://localhost'

    # test folder
    request.path = '/test/article'
    view = zeit.web.site.view_article.Article(article, request)
    assert view.meta_robots == 'noindex,follow,noarchive', (
        'wrong robots for test folder')

    # templates folder
    request.path = '/templates/article'
    view = zeit.web.site.view_article.Article(article, request)
    assert view.meta_robots == 'noindex,follow,noarchive', (
        'wrong robots for templates folder')

    # banner folder
    request.path = '/banner/article'
    view = zeit.web.site.view_article.Article(article, request)
    assert view.meta_robots == 'noindex,follow,noarchive', (
        'wrong robots for banner folder')

    # any folder
    request.path = '/any/article'
    view = zeit.web.site.view_article.Article(article, request)
    assert view.meta_robots == 'index,follow,noarchive', (
        'wrong robots for any other folder')


def test_article_doesnt_show_modified_date(testbrowser):
    select = testbrowser('/zeit-online/article/01').cssselect
    date_string = select('.metadata__date')[0].text.strip()
    assert date_string == '27. Mai 2015, 19:11 Uhr'


def test_video_in_article_is_there(testbrowser):
    article = testbrowser('/zeit-online/article/video')
    assert len(article.cssselect('.video-player__videotag')) == 1


def test_advertorial_marker_is_present(testbrowser):
    browser = testbrowser('zeit-online/article/angebot')
    assert len(browser.cssselect('.advertorial-marker')) == 1
    assert len(browser.cssselect('.advertorial-marker__title')) == 1
    assert len(browser.cssselect('.advertorial-marker__text')) == 1
    assert len(browser.cssselect('.advertorial-marker__label')) == 1


def test_canonical_url_should_omit_queries_and_hashes(testbrowser):
    browser = testbrowser('/zeit-online/article/zeit/seite-3?cid=123#comments')
    canonical_url = browser.cssselect('link[rel=canonical]')[0].get('href')
    assert canonical_url.endswith('zeit-online/article/zeit/seite-3')


def test_canonical_url_should_contain_first_page_on_full_view(testbrowser):
    browser = testbrowser('/zeit-online/article/zeit/komplettansicht')
    canonical_url = browser.cssselect('link[rel=canonical]')[0].get('href')
    assert canonical_url.endswith('zeit-online/article/zeit')


def test_zeit_article_has_correct_meta_line(testserver, selenium_driver):
    selenium_driver.get('{}/zeit-online/article/zeit'.format(testserver.url))
    dates = selenium_driver.find_elements_by_css_selector('.metadata__date')
    source = selenium_driver.find_element_by_css_selector('.metadata__source')

    assert dates[0].text == u'12. Februar 2015, 4:32 Uhr'
    assert dates[1].text == u'Editiert am 15. Februar 2015, 18:18 Uhr'
    assert source.text == u'DIE ZEIT Nr. 5/2015, 29. Januar 2015'


def test_tgs_article_has_correct_meta_line(testserver, selenium_driver):
    selenium_driver.get(
        '{}/zeit-online/article/tagesspiegel'.format(testserver.url))
    dates = selenium_driver.find_elements_by_css_selector('.metadata__date')
    source = selenium_driver.find_element_by_css_selector('.metadata__source')

    assert dates[0].text == u'15. Februar 2015, 0:00 Uhr'
    assert dates[1].text == u'Aktualisiert am 16. Februar 2015, 11:59 Uhr'
    assert source.text == u'Erschienen im Tagesspiegel'


def test_zon_article_has_correct_meta_line(testserver, selenium_driver):
    selenium_driver.get('{}/zeit-online/article/simple'.format(testserver.url))
    date = selenium_driver.find_element_by_css_selector('.metadata__date')
    source = selenium_driver.find_element_by_css_selector('.metadata__source')

    assert date.text.strip() == u'1. Juni 2015, 17:12 Uhr'
    assert source.text.strip() == u'Quelle: sid'


def test_freeform_article_has_correct_meta_line(testserver, selenium_driver):
    selenium_driver.get(
        '{}/zeit-online/article/copyrights'.format(testserver.url))
    dates = selenium_driver.find_elements_by_css_selector('.metadata__date')
    source = selenium_driver.find_element_by_css_selector('.metadata__source')

    assert dates[0].text == u'15. Februar 2015, 0:00 Uhr'
    assert dates[1].text == u'Aktualisiert am 16. Februar 2015, 11:59 Uhr'
    assert source.text == u'Quelle: ZEIT ONLINE, dpa, Reuters, rav'


def test_afp_article_has_correct_meta_line(testserver, selenium_driver):
    selenium_driver.get('{}/zeit-online/article/afp'.format(testserver.url))
    dates = selenium_driver.find_elements_by_css_selector('.metadata__date')
    source = selenium_driver.find_element_by_css_selector('.metadata__source')

    assert dates[0].text == u'15. Februar 2015, 0:00 Uhr'
    assert dates[1].text == u'Aktualisiert am 16. Februar 2015, 11:59 Uhr'
    assert source.text == u'Quelle: AFP'


def test_dpa_article_has_correct_meta_line(testbrowser):
    browser = testbrowser('/zeit-online/article/dpa')
    date = browser.cssselect('.metadata__date')[0]
    source = browser.cssselect('.metadata__source')[0]

    assert date.text.strip() == u'23. September 2015, 22:46 Uhr'
    assert source.text.strip() == u'Quelle: DPA'


def test_article_should_have_large_facebook_and_twitter_images(testbrowser):
    doc = testbrowser('/zeit-online/article/01').document
    assert doc.xpath('//meta[@property="og:image"]/@content')[0].endswith(
        'zeit-online/image/filmstill-hobbit-schlacht-fuenf-hee/wide__1300x731')
    assert doc.xpath('//meta[@name="twitter:image"]/@content')[0].endswith(
        'zeit-online/image/filmstill-hobbit-schlacht-fuenf-hee/wide__1300x731')


def test_column_article_should_have_author_as_social_media_image(testbrowser):
    doc = testbrowser('/zeit-online/article/fischer').document
    assert doc.xpath('//meta[@property="og:image"]/@content')[0].endswith(
        'zeit-online/cp-content/author_images/Julia_Zange/wide__1300x731')
    assert doc.xpath('//meta[@name="twitter:image"]/@content')[0].endswith(
        'zeit-online/cp-content/author_images/Julia_Zange/wide__1300x731')


def test_breaking_news_should_have_fallback_sharing_image(
        testbrowser, workingcopy):
    doc = testbrowser('/zeit-online/article/eilmeldungsartikel').document
    assert 'administratives/eilmeldung-share-image' in doc.xpath(
        '//meta[@property="og:image"]/@content')[0]
    assert 'administratives/eilmeldung-share-image' in doc.xpath(
        '//meta[@name="twitter:image"]/@content')[0]


def test_breaking_news_should_have_their_own_sharing_image_if_present(
        testbrowser, workingcopy):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/eilmeldungsartikel')
    with checked_out(content) as co:
        zeit.content.image.interfaces.IImages(co).image = (
            zeit.cms.interfaces.ICMSContent(
                'http://xml.zeit.de/zeit-online/image/'
                'filmstill-hobbit-schlacht-fuenf-hee'))
    doc = testbrowser('/zeit-online/article/eilmeldungsartikel').document
    assert (
        'zeit-online/image/filmstill-hobbit-schlacht-fuenf-hee' in
        doc.xpath('//meta[@property="og:image"]/@content')[0])
    assert (
        'zeit-online/image/filmstill-hobbit-schlacht-fuenf-hee' in
        doc.xpath('//meta[@name="twitter:image"]/@content')[0])


def test_article_should_evaluate_display_mode_of_image_layout(testbrowser):
    browser = testbrowser('/zeit-online/article/01')
    main_image = browser.cssselect('.article__item img')[0]
    figure = main_image.xpath('./ancestor::figure')[0]
    assert 'article__item--wide' in figure.get('class')

    browser = testbrowser('/zeit-online/article/image-column-width')
    article = browser.cssselect('main article')[0]
    figure = article.cssselect('figure[itemprop="image"]')[0]
    classname = figure.get('class')
    assert 'article__item--wide' not in classname
    assert 'article__item--rimless' not in classname
    assert 'article__item--apart' in classname


def test_missing_keyword_links_are_replaced(testbrowser):
    browser = testbrowser('/zeit-online/article/01')
    keyword = browser.cssselect('.article-tags__link')[0]
    assert keyword.get('href').endswith('/thema/wein')


def test_article_has_print_menu(testbrowser):
    browser = testbrowser('/zeit-online/article/01')
    links = browser.cssselect('.print-menu')
    assert (links[0].get('href').endswith(
        '/zeit-online/article/01?print'))


def test_multi_page_article_has_print_menu(testbrowser):
    browser = testbrowser('/zeit-online/article/tagesspiegel')
    links = browser.cssselect('.print-menu')
    assert (links[0].get('href').endswith(
        '/zeit-online/article/tagesspiegel/komplettansicht?print'))


def test_article_renders_quotes_correctly(testbrowser):
    browser = testbrowser('/zeit-online/article/quotes')
    quotes = browser.cssselect('.quote')
    assert len(quotes) == 3

    quote_with_linked_source = quotes[0]
    quote_with_source = quotes[1]
    quote_without_source = quotes[2]

    assert quote_with_linked_source.cssselect(
        '.quote__source > .quote__link[href="http://www.imdb.com/title/'
        'tt0110912/quotes?item=qt0447099"]')
    assert not quote_with_source.cssselect('.quote__source > *')
    assert not quote_without_source.cssselect('.quote__source')


def test_article_advertorial_pages_should_render_correctly(testbrowser):
    browser = testbrowser('/zeit-online/article/angebot')
    assert browser.cssselect('.advertorial-marker')
    browser = testbrowser('/zeit-online/article/angebot/seite-2')
    assert browser.cssselect('.advertorial-marker')
    browser = testbrowser('/zeit-online/article/angebot/komplettansicht')
    assert browser.cssselect('.advertorial-marker')


def test_article_should_render_quiz_in_iframe(testbrowser):
    browser = testbrowser('/zeit-online/article/quiz')
    iframe = browser.cssselect('iframe')
    assert iframe[0].get(
        'src') == 'http://quiz.zeit.de/#/quiz/103?embedded&adcontrol'
    assert iframe[1].get(
        'src') == 'http://quiz.zeit.de/#/quiz/104?embedded'


def test_instantarticle_representation_should_have_correct_content(
        testbrowser):
    bro = testbrowser('/instantarticle/zeit-online/article/quotes')

    canonical = bro.cssselect('link[rel=canonical]')[0].get('href')
    assert 'zeit-online/article/quotes' in canonical
    assert 'instantarticle' not in canonical
    assert '"Pulp Fiction"' in bro.cssselect('h1')[0].text
    assert bro.cssselect('.op-published')[0].text.strip() == '2. Juni 1999'
    assert bro.cssselect('.op-modified')[0].text.strip() == '20. Dezember 2013'
    assert bro.cssselect('figure > img[src$="square__2048x2048"]')
    assert len(bro.cssselect('aside')) == 3
    assert 'Bernie Sanders' in bro.cssselect('figcaption')[0].text
    assert u'© Warner Bros./dpa' == bro.cssselect('figcaption > cite')[0].text


def test_instantarticle_item_should_wrap_correct_article_in_cdata(testbrowser):
    browser = testbrowser(
        '/instantarticle-item/zeit-online/article/quotes')
    document = lxml.etree.fromstring(browser.contents)
    html_str = document.xpath('./*[local-name()="encoded"]/text()')[0]
    html = lxml.html.fromstring(html_str)
    canonical = html.xpath('./head/link[@rel="canonical"]/@href')[0]
    assert canonical == 'http://localhost/zeit-online/article/quotes'


def test_instantarticle_should_have_tracking_iframe(testbrowser):
    browser = testbrowser('/instantarticle/zeit-online/article/quotes')
    assert browser.cssselect('figure.op-tracker')
    assert browser.cssselect('iframe[src*="fbia/zeit-online/article/quotes"]')


def test_instantarticle_should_show_linked_author_if_available(testbrowser):
    browser = testbrowser('/instantarticle/zeit-online/article/02')
    assert browser.cssselect('address a')[0].get('href').endswith(
        '/autoren/H/Wenke_Husmann/index.xml')
    assert browser.cssselect('address a')[0].text.strip() == 'Wenke Husmann'


def test_instantarticle_should_show_author_fallback(testbrowser):
    browser = testbrowser('/instantarticle/zeit-online/article/quotes')
    assert browser.cssselect('address')[0].text.strip() == 'ZEIT ONLINE'


def test_instantarticle_should_respect_local_image_captions(testbrowser):
    browser = testbrowser('/instantarticle/zeit-online/article/quotes')
    assert browser.cssselect('figcaption')[0].text.strip().startswith(
        u'Bernie Sanders kommt Hillary Clinton gefährlich nahe.')


def test_instantarticle_should_render_empty_page_on_interrupt(testserver):
    resp = requests.get(
        testserver.url + '/instantarticle/zeit-online/article/01')
    assert 'X-Interrupt' in resp.headers
    assert len(resp.text) == 0

    resp = requests.get(
        testserver.url + '/instantarticle-item/zeit-online/article/01')
    assert 'X-Interrupt' in resp.headers
    assert len(resp.text) == 0


def test_instantarticle_should_render_ads(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set('fbia_advertising')
    browser = testbrowser(
        '/instantarticle/zeit-online/article/simple-multipage')
    assert len(browser.cssselect('iframe #iqadtile3')) == 1
    assert len(browser.cssselect('iframe #iqadtile4')) == 1
    assert len(browser.cssselect('iframe #iqadtile8')) == 1


def test_instantarticle_ads_should_include_adcontroller_values(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set('fbia_advertising')
    browser = testbrowser(
        '/instantarticle/campus/article/01-countdown-studium')
    assert 'mitte1' in browser.contents
    assert 'zeitonline,fachhochschulen,bafg,' in browser.contents
    assert '"studium",' in browser.contents
    assert '"hochschule",' in browser.contents
    assert '\'iqdzeit_fbia\'' in browser.contents


def test_zon_nextread_teaser_must_not_show_expired_image(testbrowser):
    browser = testbrowser('/zeit-online/article/simple-nextread-expired-image')
    assert len(browser.cssselect('.nextread.nextread--with-image')) == 0
    assert len(browser.cssselect('.nextread.nextread--no-image')) == 1
    assert len(browser.cssselect('.nextread figure')) == 0
    assert len(browser.cssselect('.nextread image')) == 0


def test_zon_nextread_teaser_must_not_show_image_for_column(testbrowser):
    browser = testbrowser('/zeit-online/article/simple-nextread-column')
    assert len(browser.cssselect('.nextread.nextread--with-image')) == 0
    assert len(browser.cssselect('.nextread.nextread--no-image')) == 1
    assert len(browser.cssselect('.nextread figure')) == 0
    assert len(browser.cssselect('.nextread image')) == 0


def test_nextread_should_display_date_last_published_semantic(testbrowser):
    browser = testbrowser('/zeit-online/article/simple-nextread')
    nextread_date = browser.cssselect('.nextread__dt')[0]
    assert nextread_date.text.strip() == '15. Februar 2015'


def test_article_contains_zeit_clickcounter(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set('third_party_modules')
    browser = testbrowser('/zeit-online/article/simple')
    counter = browser.cssselect('body noscript img[src^="https://cc.zeit.de"]')
    assert ("img.src = 'https://cc.zeit.de/cc.gif?banner-channel="
            "sport/article") in browser.contents
    assert len(counter) == 1
    assert ('cc.zeit.de/cc.gif?banner-channel=sport/article'
            ) in counter[0].get('src')


def test_fbia_article_contains_meta_robots(httpbrowser):
    browser = httpbrowser('/fbia/zeit-online/article/simple',
                          headers={'Host': 'fbia.zeit.de'})
    assert '<meta name="robots" content="noindex, follow">' in browser.contents


def test_fbia_article_contains_correct_webtrekk_platform(httpbrowser):
    browser = httpbrowser('/fbia/zeit-online/article/simple',
                          headers={'Host': 'fbia.zeit.de'})
    assert '25: "instant article"' in browser.contents


def test_fbia_article_contains_correct_webtrekk_contentid(httpbrowser):
    browser = httpbrowser('/fbia/zeit-online/article/simple',
                          headers={'Host': 'fbia.zeit.de'})
    assert 'wt.contentId = "redaktion.sport...article.sid|www.zeit.de\
/zeit-online/article/simple";' in browser.contents


def test_cannot_access_content_on_fbia_host(testserver):
    r = requests.get('%s/zeit-online/index' % testserver.url,
                     headers={'Host': 'fbia.zeit.de'})
    assert r.status_code == 404
    r = requests.get('%s/zeit-online/image/weltall/original' % testserver.url,
                     headers={'Host': 'fbia.zeit.de'})
    assert r.status_code == 404


def test_cannot_access_fbia_tracking_on_content_host(testserver):
    r = requests.get('%s/fbia/zeit-online/article/simple' % testserver.url,
                     headers={'Host': 'www.zeit.de'})
    assert r.status_code == 404
    r = requests.get('%s/fbia/zeit-online/article/simple' % testserver.url,
                     headers={'Host': 'fbia.zeit.de'})
    assert r.status_code == 200


def test_amp_link_should_be_present_and_link_to_the_correct_amp(testbrowser):
    browser = testbrowser('/zeit-online/article/zeit')
    amp_link = browser.cssselect('link[rel=amphtml]')
    assert amp_link
    amp_url = amp_link[0].get('href')
    assert amp_url.endswith('amp/zeit-online/article/zeit')

    browser = testbrowser('/zeit-online/article/zeit/seite-2')
    amp_link = browser.cssselect('link[rel=amphtml]')
    assert amp_link
    amp_url = amp_link[0].get('href')
    assert amp_url.endswith('amp/zeit-online/article/zeit')


@pytest.mark.parametrize(
    'parameter', [
        ('/amp/zeit-online/article/cardstack'),
        ('/amp/zeit-online/article/quiz'),
        ('/amp/zeit-online/article/raw_code')
    ])
def test_amp_article_placeholder(testbrowser, parameter):
    select = testbrowser(parameter).cssselect
    assert len(select('.article__placeholder')) >= 1


def test_newsletter_optin_page_has_webtrekk_ecommerce(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set('third_party_modules')
    browser = testbrowser(
        '/zeit-online/article/simple?newsletter-optin=elbVertiefung-_!1:2')
    assert '8: \'elbvertiefung-_1_2\'' in browser.contents


def test_no_webtrekk_ecommerce_without_newsletter_optin(testbrowser):
    browser = testbrowser(
        '/zeit-online/article/simple?newsletter-optin')
    assert 'wt.customEcommerceParameter' not in browser.contents

    browser = testbrowser(
        '/zeit-online/article/simple')
    assert 'wt.customEcommerceParameter' not in browser.contents


def test_article_contains_webtrekk_parameter_asset(dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/cardstack')
    view = zeit.web.site.view_article.Article(context, dummy_request)
    assert view.webtrekk['customParameter']['cp27'] == 'cardstack.2/seite-1'

    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/embed-header-video')
    view = zeit.web.site.view_article.Article(context, dummy_request)
    assert view.webtrekk['customParameter']['cp27'] == 'video.header/seite-1'

    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/embed-header-quiz')
    view = zeit.web.site.view_article.Article(context, dummy_request)
    assert view.webtrekk['customParameter']['cp27'] == 'quiz.header/seite-1'

    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/embed-header-cardstack')
    view = zeit.web.site.view_article.Article(context, dummy_request)
    assert view.webtrekk['customParameter']['cp27'] == (
        'cardstack.header/seite-1')

    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/embed-header-raw')
    view = zeit.web.site.view_article.Article(context, dummy_request)
    assert view.webtrekk['customParameter']['cp27'] == 'raw.header/seite-1'

    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/video-expired')
    view = zeit.web.site.view_article.Article(context, dummy_request)
    assert view.webtrekk['customParameter']['cp27'] == ''

    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/amp-invalid')
    view = zeit.web.site.view_article.Article(context, dummy_request)
    assert view.webtrekk['customParameter']['cp27'] == \
        'cardstack.2/seite-1;' \
        'quiz.3/seite-1;raw.4/seite-1;rawtext.5/seite-1'


def test_advertorial_article_contains_correct_webtrekk_param(dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/angebot')
    view = zeit.web.site.view_article.Article(context, dummy_request)
    assert view.webtrekk['customParameter']['cp26'] == 'article.advertorial'


def test_article_contains_serie_and_genre_in_webtrekk_param(dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    view = zeit.web.site.view_article.Article(context, dummy_request)
    assert view.webtrekk['customParameter']['cp26'] == 'article.serie.glosse'


def test_article_has_image_header_embed(testbrowser):
    browser = testbrowser('/zeit-online/article/embed-header-image')
    embed = browser.cssselect('.article-embed')[0]
    assert len(embed.cssselect('.article__media-item')) == 1


def test_article_has_video_header_embed(testbrowser):
    browser = testbrowser('/zeit-online/article/embed-header-video')
    embed = browser.cssselect('.article-embed')[0]
    assert len(embed.cssselect('.video-player')) == 1


def test_article_has_quiz_header_embed(testbrowser):
    browser = testbrowser('/zeit-online/article/embed-header-quiz')
    embed = browser.cssselect('.article-embed')[0]
    assert len(embed.cssselect('.quiz')) == 1


def test_article_has_raw_header_embed(testbrowser):
    browser = testbrowser('/zeit-online/article/embed-header-raw')
    embed = browser.cssselect('.article-embed')[0]
    assert len(embed.cssselect('.raw')) == 1


def test_article_in_series_has_banner(testbrowser):
    browser = testbrowser('/zeit-online/article/01')

    assert len(browser.cssselect('.article-series')) == 1

    title = browser.cssselect('.article-series__title')[0].text.strip()
    assert title == '70 Jahre DIE ZEIT'

    browser = testbrowser('/zeit-online/article/02')

    assert len(browser.cssselect('.article-series')) == 1

    title = browser.cssselect('.article-series__title')[0].text.strip()
    assert title == 'Geschafft!'


def test_article_in_series_has_banner_image(testbrowser):
    browser = testbrowser('/zeit-online/article/01')
    figure = browser.cssselect('.article-series__media')
    image = figure[0].cssselect('img')[0]

    assert len(figure) == 1
    assert image.get('data-ratio') == '12.25'


def test_article_in_series_has_correct_link(testbrowser):
    browser = testbrowser('/zeit-online/article/01')

    url = browser.cssselect('.article-series__heading')[0].get('href')
    assert url.endswith('/serie/70-jahre-zeit')

    browser = testbrowser('/zeit-online/article/02')

    url = browser.cssselect('.article-series__heading')[0].get('href')
    assert url.endswith('/serie/geschafft')


def test_article_in_series_has_no_fallback_image(testbrowser):
    browser = testbrowser('/zeit-online/article/02')

    assert len(browser.cssselect('.article-series__media')) == 0


def test_article_without_series_has_no_banner(testbrowser):
    browser = testbrowser('/zeit-online/article/simple')

    assert len(browser.cssselect('.article-series')) == 0


def test_article_in_series_with_embed_header_has_no_banner(testbrowser):
    browser = testbrowser('/zeit-online/article/serie-cardstack')

    assert len(browser.cssselect('.article-series')) == 0


def test_podcast_article_in_series_without_image_uses_fallback_image(
        testbrowser):
    browser = testbrowser('/zeit-online/article/podcast-header-serie')
    teaser_image = browser.cssselect(".article-heading__media-item")[0]
    assert (
        'zeit-online/image/podcast-illustration-fallback/'
        in teaser_image.get('src'))


def test_podcast_article_in_series_with_image_uses_own_image(testbrowser):
    browser = testbrowser('/zeit-online/article/podcast-header')
    teaser_image = browser.cssselect(".article-heading__media-item")[0]
    assert 'zeit-online/image/podcast-illustration/' in teaser_image.get('src')


def test_liveblog_in_series_has_no_banner(testbrowser):
    browser = testbrowser('/zeit-online/article/serie-liveblog')

    assert len(browser.cssselect('.article-series')) == 0


def test_eilmeldung_in_series_has_no_banner(testbrowser):
    browser = testbrowser('/zeit-online/article/serie-eilmeldung')

    assert len(browser.cssselect('.article-series')) == 0


def test_article_in_series_with_column_attribute_has_no_banner(testbrowser):
    browser = testbrowser('/zeit-online/article/fischer')

    assert len(browser.cssselect('.article-series')) == 0


def test_article_should_not_render_expired_video(testbrowser):
    browser = testbrowser('/zeit-online/article/video-expired')
    articlepage = browser.cssselect('.article-page')
    articleitems = articlepage[0].getchildren()
    assert len(articleitems) == 2


def test_comment_count_in_metadata_not_shown_when_comments_disabled(
        testbrowser, workingcopy):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    with zeit.cms.checkout.helper.checked_out(article) as co:
        co.commentSectionEnable = False
    browser = testbrowser('/zeit-online/article/01')
    assert not browser.cssselect('.metadata__commentcount')


def test_comment_count_in_nextread_not_shown_when_comments_disabled(
        testbrowser, workingcopy):
    id = 'http://xml.zeit.de/zeit-online/article/01'
    article = zeit.cms.interfaces.ICMSContent(id)
    with zeit.cms.checkout.helper.checked_out(article) as co:
        co.commentSectionEnable = False
    with mock.patch(
            'zeit.web.core.comments.Community.get_comment_counts') as counts:
        counts.return_value = {id: 35}
        browser = testbrowser('/zeit-online/article/02')
    assert not browser.cssselect('.nextread__commentcount')


def test_article_toc_is_printed_before_paragraphs_and_lists(testbrowser):
    browser = testbrowser('/zeit-online/article/paginated')
    page = browser.cssselect('.article-page')[0]
    first_child = page.cssselect('*:first-child')[0]

    assert 'article-toc' in first_child.get('class')
    assert page.cssselect('.article-toc + p.paragraph')

    browser = testbrowser('/zeit-online/article/paginated/seite-2')
    page = browser.cssselect('.article-page')[0]
    first_child = page.cssselect('*:first-child')[0]

    assert 'article-toc' in first_child.get('class')
    assert page.cssselect('.article-toc + ul.list')

    browser = testbrowser('/zeit-online/article/paginated/seite-3')
    page = browser.cssselect('.article-page')[0]
    first_child = page.cssselect('*:first-child')[0]

    assert 'article-toc' in first_child.get('class')
    assert page.cssselect('.article-toc + ol.list')


def test_infographics_should_display_header_above_image(testbrowser):
    browser = testbrowser('/zeit-online/article/infographic')
    items = list(browser.cssselect('.infographic__media')[0].iterchildren())
    assert 'Die Entschlackung' == items[0].text
    assert (
        u'Potenzial der Bertelsmann-Geschäfte (in Prozent des Umsatzes)' ==
        items[1].text)


def test_infographics_should_display_origin_instead_of_caption(testbrowser):
    browser = testbrowser('/zeit-online/article/infographic')
    infographic = browser.cssselect('.infographic')[0]
    caption = infographic.cssselect('figcaption')[0]
    assert 'Quelle: Statistisches Bundesamt' == caption.text.strip()


def test_infographics_should_render_html_correctly(
        tplbrowser, dummy_request):
    template = 'zeit.web.core:templates/inc/blocks/infographic.html'
    image = zeit.web.core.image.Image(mock.Mock())
    image.ratio = 1
    image.group = mock.Mock()
    image.group.master_image_for_viewport.return_value = None
    image.group.variant_url.return_value = '/foo'
    image.figure_mods = ('FOO', 'BAR', 'BAZ')

    # all border styles present
    image.origin = True
    image.copyrights = {'text': 'FOO'}
    image.caption = True
    browser = tplbrowser(template, block=image, request=dummy_request)
    assert browser.cssselect('.infographic__text')
    assert browser.cssselect('.infographic__caption')
    assert browser.cssselect('.infographic__media.high-resolution')

    # borderless subheadline
    image.caption = False
    browser = tplbrowser(template, block=image, request=dummy_request)
    assert not browser.cssselect('.infographic__text')

    # footer has border
    image.origin = True
    image.copyrights = {}
    browser = tplbrowser(template, block=image, request=dummy_request)
    assert browser.cssselect('.infographic__caption')

    image.origin = False
    image.copyrights = {'text': 'FOO'}
    browser = tplbrowser(template, block=image, request=dummy_request)
    assert browser.cssselect('.infographic__caption')

    # no border styles present
    image.copyrights = {}
    image.origin = False
    image.caption = False
    browser = tplbrowser(template, block=image, request=dummy_request)
    assert not browser.cssselect('.infographic__text')
    assert not browser.cssselect('.infographic__caption')


def test_infographics_desktop_should_have_proper_asset_source(
        testserver, selenium_driver):
    selenium_driver.set_window_size(1280, 768)
    selenium_driver.get(
        '{}/zeit-online/article/infographic'.format(testserver.url))
    img_src = selenium_driver.find_element_by_css_selector(
        '.infographic img').get_attribute('src')
    assert u'/zeit-online/image/bertelsmann-infographic/' \
           u'original__820x507__desktop' in img_src


def test_infographics_mobile_should_have_proper_asset_source(
        testserver, selenium_driver):
    selenium_driver.set_window_size(767, 1280)
    selenium_driver.get(
        '{}/zeit-online/article/infographic'.format(testserver.url))
    img_src = selenium_driver.find_element_by_css_selector(
        '.infographic img').get_attribute('src')
    assert u'/zeit-online/image/bertelsmann-infographic/' \
           u'original__450x563__mobile' in img_src


def test_contentad_is_rendered_once_on_article_pages(testbrowser):
    selector = '#iq-artikelanker'

    browser = testbrowser('/zeit-online/article/fischer')
    assert len(browser.cssselect(selector)) == 1

    browser = testbrowser('/zeit-online/article/fischer/seite-2')
    assert len(browser.cssselect(selector)) == 1

    browser = testbrowser('/zeit-online/article/fischer/komplettansicht')
    assert len(browser.cssselect(selector)) == 1


def test_zplus_badge_should_be_rendered_on_nextread(testbrowser):
    browser = testbrowser('/zeit-online/article/simple-nextread-zplus')

    zplus_badge = browser.cssselect('.nextread__kicker-logo--zplus')
    assert len(zplus_badge) == 1

    link = browser.cssselect('.nextread__link')
    assert len(link) == 1
    data_id = link[0].get('data-id')
    assert data_id == 'articlebottom.editorial-nextread...area-zplus'


def test_zplus_badge_should_be_rendered_on_nextread_register(testbrowser):
    browser = testbrowser('/zeit-online/article/simple-nextread-register')

    reg_badge = browser.cssselect('.nextread__kicker-logo--zplus-register')
    assert len(reg_badge) == 1

    link = browser.cssselect('.nextread__link')
    assert len(link) == 1
    data_id = link[0].get('data-id')
    assert data_id == 'articlebottom.editorial-nextread...area-zplus-register'


def test_article_byline_is_displayed_completely(testbrowser):
    browser = testbrowser('/zeit-online/article/01')
    dom_node_byline = browser.cssselect('.byline')
    assert len(dom_node_byline) == 1
    raw_inner_html = dom_node_byline[0].text_content().replace("\n", "")
    assert " ".join(raw_inner_html.split()) == \
           'Eine Glosse von Wenke Husmann, Jochen Bittner,' \
           ' Heike Jahberg und Jasper Riemann'


def test_video_in_article_has_poster_copyright(testbrowser):
    browser = testbrowser('/zeit-online/article/video')
    video = browser.cssselect('figure[data-video-size]')[0]
    figure_copyright = video.cssselect('.figure__copyright')
    assert len(figure_copyright) == 1
    copyright_person = figure_copyright[0].cssselect('[itemprop="name"]')[0]
    assert copyright_person.text == u'© Foto: Alaa Al-Marjani/Reuters'


def test_zplus_zon_article_has_correct_markup(testbrowser):
    browser = testbrowser('/zeit-online/article/zplus-zon')

    zplus_box = browser.cssselect('.zplus-badge--coverless')
    assert len(zplus_box) == 1

    zplus_banner = zplus_box[0].cssselect('.zplus-badge__banner')
    zplus_icon = zplus_box[0].cssselect('.zplus-badge__icon')
    zplus_text = zplus_box[0].cssselect('.zplus-badge__text')
    zplus_link = zplus_box[0].cssselect('.zplus-badge__link-text')
    zplus_modifier = browser.cssselect('.article__item--has-badge')

    assert len(zplus_modifier) == 2
    assert len(zplus_banner) == 1
    assert len(zplus_icon) == 1
    assert len(zplus_text) == 1
    assert len(zplus_link) == 1
    assert ('exklusive-zeit-artikel' in
            zplus_box[0].cssselect('a')[0].get('href'))
    assert 'Exklusiv' in zplus_link[0].text.strip()
    assert not zplus_box[0].cssselect('.zplus-badge__media')


def test_zplus_volumeless_print_article_has_zplus_zon_badge(testbrowser):
    browser = testbrowser('/zeit-online/article/zplus-novolume')

    zplus_box = browser.cssselect('.zplus-badge--coverless')
    assert len(zplus_box) == 1

    zplus_banner = zplus_box[0].cssselect('.zplus-badge__banner')
    zplus_badge = zplus_box[0].cssselect('.zplus-badge__icon')
    zplus_modifier = browser.cssselect('.article__item--has-badge')

    assert len(zplus_modifier) == 2
    assert len(zplus_banner) == 1
    assert len(zplus_badge) == 1
    assert not zplus_box[0].cssselect('.zplus-badge__media')


def test_zplus_coverless_print_article_has_fallback_image(testbrowser):
    browser = testbrowser('/zeit-online/article/zplus-nocover')

    zplus_box = browser.cssselect('.zplus-badge')
    assert len(zplus_box) == 1

    zplus_media = zplus_box[0].cssselect('.zplus-badge__media-item')
    assert 'default_packshot_diezeit' in zplus_media[0].get('src')

    text = zplus_box[0].cssselect('.zplus-badge__text')[0]
    assert 'ZEIT Nr. 03/2016' in text.text_content()


def test_zplus_abo_print_article_has_correct_markup(testbrowser):
    browser = testbrowser('/zeit-online/article/zplus-zeit')

    zplus_box = browser.cssselect('.zplus-badge')
    assert len(zplus_box) == 1

    zplus_banner = zplus_box[0].cssselect('.zplus-badge__banner')
    zplus_icon = zplus_box[0].cssselect('.zplus-badge__icon')
    zplus_text = zplus_box[0].cssselect('.zplus-badge__text')
    zplus_cover = zplus_box[0].cssselect('.zplus-badge__media')
    zplus_media = zplus_box[0].cssselect('.zplus-badge__media-item')
    zplus_link = zplus_box[0].cssselect('.zplus-badge__link')
    zplus_link_text = zplus_box[0].cssselect('.zplus-badge__link-text')
    zplus_modifier = browser.cssselect('.article__item--has-badge')

    assert len(zplus_modifier) == 2
    assert len(zplus_banner) == 1
    assert len(zplus_icon) == 1
    assert len(zplus_text) == 1
    assert len(zplus_cover) == 1
    assert len(zplus_media) == 1
    assert len(zplus_link_text) == 1
    assert zplus_link[0].get('href').startswith('http://localhost/2015/05')
    assert zplus_link_text[0].text == u'Exklusiv für Abonnenten'
    assert zplus_media[0].get('src').startswith(
        'http://localhost/zeit-online/image/zeitcover/original')


def test_zplus_print_article_has_correct_markup(testbrowser):
    browser = testbrowser('/zeit-online/article/zplus-zeit-register')

    zplus_box = browser.cssselect('.zplus-badge')
    assert len(zplus_box) == 1

    article_metadata_source = browser.cssselect('.metadata__source')
    zplus_banner = zplus_box[0].cssselect('.zplus-badge__banner')
    zplus_icon = zplus_box[0].cssselect('.zplus-badge__icon')
    zplus_text = zplus_box[0].cssselect('.zplus-badge__text')
    zplus_cover = zplus_box[0].cssselect('.zplus-badge__media')
    zplus_media = zplus_box[0].cssselect('.zplus-badge__media-item')
    zplus_link = zplus_box[0].cssselect('.zplus-badge__link')
    zplus_link_text = zplus_box[0].cssselect('.zplus-badge__link-text')
    zplus_intro = zplus_box[0].cssselect('.zplus-badge__intro')
    zplus_modifier = browser.cssselect('.article__item--has-badge')

    assert len(article_metadata_source) == 1
    assert len(zplus_modifier) == 2
    assert len(zplus_banner) == 1
    assert len(zplus_icon) == 0
    assert len(zplus_text) == 1
    assert len(zplus_cover) == 1
    assert len(zplus_media) == 1
    assert len(zplus_link_text) == 1
    assert len(zplus_intro) == 1
    assert zplus_link[0].get('href').startswith('http://localhost/2015/05')
    assert zplus_link_text[0].text == 'ZEIT Nr. 05/2015'
    assert zplus_intro[0].text == 'Aus der'
    assert zplus_media[0].get('src').startswith(
        'http://localhost/zeit-online/image/zeitcover/original')


def test_zplus_print_article_has_correct_markup_if_reader_revenue_off(
        testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.unset('reader_revenue')
    browser = testbrowser('/zeit-online/article/zplus-zeit-register')
    article_metadata_source = browser.cssselect('.metadata__source')
    assert article_metadata_source.__len__() == 1


def test_zplus_comments_under_register_article(testbrowser):
    c1_param = '?C1-Meter-Status=paywall&C1-Meter-User-Status=anonymous'
    path = '/zeit-online/article/zplus-zeit-register'
    url = '{}{}'.format(path, c1_param)
    browser = testbrowser(url)

    assert len(browser.cssselect('.paragraph--faded')) == 1
    assert len(browser.cssselect('.gate')) == 1
    assert len(browser.cssselect('.comment-section')) == 1


def test_zplus_comments_not_under_abo_article(testbrowser):
    c1_param = '?C1-Meter-Status=always_paid'
    path = '/zeit-online/article/zplus-zeit'
    url = '{}{}'.format(path, c1_param)
    browser = testbrowser(url)

    assert len(browser.cssselect('.comment-section')) == 0


def test_free_print_article_has_volume_badge(testbrowser):
    browser = testbrowser('/zeit-online/article/zplus-zeit-free')
    badge = browser.cssselect('main article .zplus-badge')[0]
    label = badge.cssselect('.zplus-badge__text')[0]
    link = badge.cssselect('.zplus-badge__link')[0]

    assert ' '.join(label.text_content().split()) == 'Aus der ZEIT Nr. 05/2015'
    assert link.get('href').startswith('http://localhost/2015/05')
    assert badge.cssselect('.zplus-badge__media')

    # test volume badge is in single page view too
    browser = testbrowser(
        '/zeit-online/article/zplus-zeit-free/komplettansicht')

    assert browser.cssselect('main article .zplus-badge')


def test_free_print_article_shows_no_volume_badge_on_page_two(testbrowser):
    browser = testbrowser('/zeit-online/article/zplus-zeit-free/seite-2')

    assert not browser.cssselect('main article .zplus-badge')


def test_registration_zon_article_has_no_zplus_badge(testbrowser):
    browser = testbrowser('/zeit-online/article/zplus-zon-register')

    assert not browser.cssselect('.zplus-badge')
    assert not browser.cssselect('.article__item--has-badge')


def test_free_article_has_no_zplus_badge(testbrowser):
    browser = testbrowser('/zeit-online/article/simple')

    assert not browser.cssselect('.zplus-badge')
    assert not browser.cssselect('.article__item--has-badge')


def test_zplus_volume_cover_should_track_link_with_product_id(testbrowser):
    browser = testbrowser('/zeit-online/article/zplus-zeit')
    assert browser.cssselect('.zplus-badge__link')[0].get('href') == (
        'http://localhost/2015/05?wt_zmc=fix.int.zonpme.zeitde.wall_abo.'
        'premium.packshot.cover.zei&utm_medium=fix&utm_source=zeitde_zon'
        'pme_int&utm_campaign=wall_abo&utm_content=premium_packshot_cover_zei')


def test_volume_teaser_is_rendered_correctly(testbrowser):
    browser = testbrowser('/zeit-online/article/volumeteaser')
    volume_teaser = browser.cssselect('.volume-teaser')
    volume_teaser_link = browser.cssselect(
        '.volume-teaser__link')[0]
    assert len(volume_teaser) == 1
    assert (
        volume_teaser_link.get('href') ==
        'https://premium.zeit.de/abo/diezeit/2016/01')
    assert (
        u'Dieser Artikel stammt aus der ZEIT Nr. 01/2016. '
        u'Hier können Sie die gesamte Ausgabe lesen.'
        in volume_teaser_link.text)


def test_volume_teaser_display_correct_image_on_desktop(
        testserver, selenium_driver):
    selenium_driver.set_window_size(1280, 768)
    selenium_driver.get(
        '{}/zeit-online/article/volumeteaser'.format(testserver.url))
    img_src = selenium_driver.find_element_by_css_selector(
        '[data-src*="test-printcover"]').get_attribute('src')
    assert u'2016-09/test-printcover/original__220x157__desktop' in img_src


def test_share_buttons_are_present(testbrowser):
    browser = testbrowser('/zeit-online/article/simple')
    canonical = browser.cssselect('link[rel="canonical"]')[0].get('href')
    sharing_menu = browser.cssselect('.sharing-menu')[0]
    links = sharing_menu.cssselect('.sharing-menu__link')
    labels = sharing_menu.cssselect('.sharing-menu__text')

    #  facebook
    parts = urlparse.urlparse(links[0].get('href'))
    query = urlparse.parse_qs(parts.query)
    url = query.get('u').pop(0)
    assert 'wt_zmc=sm.ext.zonaudev.facebook.ref.zeitde.share.link' in url
    assert 'utm_medium=sm' in url
    assert 'utm_source=facebook_zonaudev_ext' in url
    assert 'utm_campaign=ref' in url
    assert 'utm_content=zeitde_share_link_x' in url

    #  twitter
    parts = urlparse.urlparse(links[1].get('href'))
    query = urlparse.parse_qs(parts.query)
    assert query.get('text').pop(0) == (
        'Williams wackelt weiter, steht aber im Viertelfinale')
    assert query.get('via').pop(0) == 'zeitonline'
    assert 'share' in query.get('url').pop(0)

    #  flipboard
    parts = urlparse.urlparse(links[2].get('href'))
    query = urlparse.parse_qs(parts.query)
    assert query.get('title').pop(0) == (
        'Williams wackelt weiter, steht aber im Viertelfinale')
    assert 'share' in query.get('url').pop(0)

    #  whatsapp
    parts = urlparse.urlparse(links[3].get('href'))
    query = urlparse.parse_qs(parts.query)
    assert ('Williams wackelt weiter, steht aber im Viertelfinale - '
            'Artikel auf ZEIT ONLINE: ') in query.get('text').pop(0)

    #  facebook messenger
    parts = urlparse.urlparse(links[4].get('href'))
    query = urlparse.parse_qs(parts.query)
    assert query.get('link').pop(0).startswith(canonical)
    assert query.get('app_id').pop(0) == '638028906281625'

    #  mail
    parts = urlparse.urlparse(links[5].get('href'))
    query = urlparse.parse_qs(parts.query)
    assert ('Williams wackelt weiter, steht aber im Viertelfinale - '
            'Artikel auf ZEIT ONLINE') in query.get('subject').pop(0)
    assert 'Artikel auf ZEIT ONLINE lesen:' in query.get('body').pop(0)

    assert labels[0].text == 'Facebook'
    assert labels[1].text == 'Twittern'
    assert labels[2].text == 'Flippen'
    assert labels[3].text == 'WhatsApp'
    assert labels[4].text == 'Facebook Messenger'
    assert labels[5].text == 'Mailen'


def test_merian_link_has_nofollow(testbrowser, dummy_request):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/simple-merian-nofollow')
    view = zeit.web.site.view_article.Article(article, dummy_request)
    assert view.product_id == 'merian'

    browser = testbrowser('/zeit-online/article/simple-merian-nofollow')
    sourcelink = browser.cssselect('.metadata__source a')[0]
    assert sourcelink.get('rel') == 'nofollow'


def test_article_contains_authorbox(testbrowser):
    browser = testbrowser('/zeit-online/article/authorbox')
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


@pytest.mark.parametrize('c1_parameter', [
    '?C1-Meter-Status=paywall&C1-Meter-User-Status=anonymous',
    '?C1-Meter-Status=paywall&C1-Meter-User-Status=registered',
    '?C1-Meter-Status=always_paid'])
def test_paywall_switch_showing_forms(c1_parameter, testbrowser):
    urls = [
        'zeit-online/article/zeit',
        'zeit-online/article/zeit/seite-2',
        'zeit-online/article/zeit/komplettansicht',
        'zeit-online/article/fischer'
    ]

    for url in urls:
        browser = testbrowser(
            '{}{}'.format(url, c1_parameter))
        assert len(browser.cssselect('.paragraph--faded')) == 1
        assert len(browser.cssselect('.gate')) == 1
        assert len(browser.cssselect(
            '.gate--register')) == int('anonymous' in c1_parameter)


def test_paywall_adds_premium_redirect_target(testbrowser):
    browser = testbrowser(
        '/zeit-online/article/zeit?C1-Meter-Status=always_paid')
    input = browser.cssselect('form.gate__form input[name="url"]')[0]
    premium_url = input.get('value')
    assert (
        premium_url == 'https://premium.zeit.de/abo/paywall?url='
        'http%3A%2F%2Flocalhost%2Fzeit-online%2Farticle%2Fzeit'
        '%23success-registration')


def test_free_article_has_correct_ivw_code(dummy_request):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    view = zeit.web.site.view_article.Article(article, dummy_request)
    assert view.ivw_code == 'kultur/film/bild-text'


def test_free_article_without_ressort_has_correct_ivw_code(dummy_request):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/simple')
    view = zeit.web.site.view_article.Article(article, dummy_request)
    view.ressort = ''
    assert view.ivw_code == 'administratives/bild-text'


def test_free_article_without_sub_ressort_has_correct_ivw_code(dummy_request):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/simple')
    view = zeit.web.site.view_article.Article(article, dummy_request)
    view.sub_ressort = None
    assert view.ivw_code == 'sport/bild-text'


def test_paid_subscription_article_has_correct_ivw_code(dummy_request):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/zplus-zeit')
    view = zeit.web.site.view_article.Article(article, dummy_request)
    assert view.ivw_code == 'kultur/film/bild-text/paid'


def test_not_paid_subscription_article_has_correct_ivw_code(dummy_request):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/zplus-zeit')
    dummy_request.GET['C1-Meter-Status'] = 'always_paid'
    view = zeit.web.site.view_article.Article(article, dummy_request)
    assert view.ivw_code == 'kultur/film/bild-text'


def test_invalid_paywall_status_is_ignored(testbrowser):
    browser = testbrowser(
        '/zeit-online/article/zplus-zeit?C1-Meter-Status=wurstbrot')
    assert len(browser.cssselect('.paragraph--faded')) == 0


def test_paywall_get_param_works_like_http_header(testbrowser):

    browser_with_header = testbrowser()
    browser_with_header.addHeader('C1-Meter-Status', 'always_paid')
    browser_with_header.open(
        '/zeit-online/article/zplus-zeit?C1-Meter-Status=wurstbrot')

    browser_with_getparam = testbrowser(
        '/zeit-online/article/zplus-zeit?C1-Meter-Status=always_paid')

    assert browser_with_getparam.contents == browser_with_header.contents


def test_overscrolling_is_active(selenium_driver, testserver):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    conf['overscrolling_active'] = True
    driver = selenium_driver
    driver.set_window_size(1200, 900)
    driver.get(
        '%s/zeit-online/article/01' % testserver.url)
    footer = driver.find_element_by_class_name('footer')
    driver.execute_script(
        "return arguments[0].scrollIntoView();window.scrollBy(0,100)", footer)
    condition = expected_conditions.visibility_of_element_located((
        By.CSS_SELECTOR, '#overscrolling'))
    assert WebDriverWait(
        selenium_driver, 1).until(condition)


def test_overscrolling_is_not_active_on_paywalls(selenium_driver, testserver):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    conf['overscrolling_active'] = True
    driver = selenium_driver
    driver.set_window_size(1200, 900)
    path = 'zeit-online/article/01'
    query = 'C1-Meter-Status=paywall&C1-Meter-User-Status=register'
    driver.get('{}/{}?{}'.format(testserver.url, path, query))
    footer = driver.find_element_by_class_name('footer')
    driver.execute_script(
        "return arguments[0].scrollIntoView();window.scrollBy(0,100)", footer)
    condition = expected_conditions.invisibility_of_element_located((
        By.CSS_SELECTOR, '#overscrolling'))
    assert WebDriverWait(
        selenium_driver, 1).until(condition)


def test_overscrolling_is_not_active_on_non_destop_environment(
        selenium_driver, testserver):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    conf['overscrolling_active'] = True
    driver = selenium_driver
    driver.set_window_size(760, 900)
    path = 'zeit-online/article/01'
    query = 'C1-Meter-Status=paywall&C1-Meter-User-Status=register'
    driver.get('{}/{}?{}'.format(testserver.url, path, query))
    footer = driver.find_element_by_class_name('footer')
    driver.execute_script(
        "return arguments[0].scrollIntoView();window.scrollBy(0,100)", footer)
    condition = expected_conditions.invisibility_of_element_located((
        By.CSS_SELECTOR, '#overscrolling'))
    assert WebDriverWait(
        selenium_driver, 1).until(condition)


def test_overscrolling_is_working_as_expected(selenium_driver, testserver):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    conf['overscrolling_active'] = True
    driver = selenium_driver
    driver.set_window_size(1200, 900)
    driver.get(
        '%s/zeit-online/article/01' % testserver.url)
    footer = driver.find_element_by_class_name('footer')
    driver.execute_script(
        "return arguments[0].scrollIntoView();window.scrollBy(0,100)", footer)
    condition = expected_conditions.visibility_of_element_located((
        By.CSS_SELECTOR, '#overscrolling'))
    assert WebDriverWait(
        selenium_driver, 1).until(condition)
    driver.execute_script('window.scrollBy(0, 801)')
    condition = expected_conditions.visibility_of_element_located((
        By.CSS_SELECTOR, 'body[data-is-hp="true"]'))
    assert WebDriverWait(
        selenium_driver, 5).until(condition)
    # overscrolling is inactive in app
    driver.get(
        '%s/zeit-online/article/01?app-content' % testserver.url)
    footer = driver.find_element_by_class_name('footer')
    driver.execute_script(
        "return arguments[0].scrollIntoView();window.scrollBy(0,100)", footer)
    condition = expected_conditions.invisibility_of_element_located((
        By.CSS_SELECTOR, '#overscrolling'))
    assert WebDriverWait(
        selenium_driver, 1).until(condition)


def test_overscrolling_is_turned_off_by_configuration(
        selenium_driver, testserver):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    conf['overscrolling_active'] = True
    driver = selenium_driver
    driver.set_window_size(1200, 900)
    driver.get(
        '%s/zeit-online/article/01' % testserver.url)
    footer = driver.find_element_by_class_name('footer')
    driver.execute_script(
        "return arguments[0].scrollIntoView();window.scrollBy(0,100)", footer)
    condition = expected_conditions.invisibility_of_element_located((
        By.CSS_SELECTOR, '#overscrolling'))
    assert WebDriverWait(
        selenium_driver, 1).until(condition)


def test_paywall_returns_correct_first_click_free_to_webtrekk(
        application, dummy_request):

    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/simple')
    view = zeit.web.site.view_article.Article(content, dummy_request)
    assert view.webtrekk['customParameter']['cp29'] == 'unfeasible'

    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/zplus-zeit-register')
    view = zeit.web.site.view_article.Article(content, dummy_request)
    assert view.webtrekk['customParameter']['cp29'] == 'no'

    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/zplus-zeit-register')
    dummy_request.GET['C1-Meter-Status'] = 'open'
    dummy_request.GET['C1-Meter-Info'] = 'first_click_free'
    view = zeit.web.site.view_article.Article(content, dummy_request)
    assert view.webtrekk['customParameter']['cp29'] == 'yes'


def test_nextread_shows_zmo_kicker_logo_and_styles(testbrowser):
    browser = testbrowser('/zeit-online/article/simple-nextread-zmo')
    nextread = browser.cssselect('article.nextread')[0]
    assert nextread.cssselect('.nextread__kicker--zmo')
    assert nextread.cssselect('.nextread__kicker-logo--zmo')


@pytest.mark.skipif(True,
                    reason="We need a way to mock liveblog in tests")
def test_liveblog_article_uses_esi(selenium_driver, testserver):
    selenium_driver.get(
        '{}/zeit-online/cp-content/liveblog-offline'.format(testserver.url))
    blog = WebDriverWait(selenium_driver, 15).until(
        expected_conditions.presence_of_element_located(
            (By.ID, "livedesk-root")))
    assert blog.is_displayed(), 'ESI Liveblog not displayed'


def test_zplus_badge_is_zeit_on_print_insert(testbrowser):
    browser = testbrowser('/zeit-online/article/zeit-geld-print-insert')
    assert len(browser.cssselect(
        '.zplus-badge__media-item[src$="/printcover/original"]')) == 1
    assert len(
        browser.cssselect('.volume-teaser__media-item'
                          '[src$="/printcover-beilage-geld/original"]')) == 1


def test_article_should_not_include_itunes_smart_app_banner(testbrowser):
    browser = testbrowser('/zeit-online/article/simple')
    app_banner_id = browser.cssselect('meta[name="apple-itunes-app"]')
    assert len(app_banner_id) == 0


def test_zplus_badge_has_no_link_if_volumes_unpublished(
        testbrowser, monkeypatch):
    monkeypatch.setattr(
        zeit.web.core.view_article.Article, 'volumepage_is_published', False)
    browser = testbrowser('/zeit-online/article/zplus-zeit')
    assert not browser.cssselect('.zplus-badge__link')


def test_advertorial_has_no_home_button_as_pagination(testbrowser):
    browser = testbrowser('/zeit-online/article/advertorial-onepage')
    assert len(browser.cssselect('.article-pagination__link')) == 0


def test_narrow_header_should_render_image_column_width(testbrowser):
    browser = testbrowser('/zeit-online/article/narrow')
    figure = browser.cssselect('.article-header figure')[0]
    assert 'article__item--wide' not in figure.get('class')
    assert 'article__item--apart' in figure.get('class')


def test_abo_paywall_schema_attr(testbrowser):
    browser = testbrowser('/zeit-online/article/zplus-zon')
    jsonld = browser.cssselect('script[type="application/ld+json"]')
    assert len(jsonld) == 1
    jsonld = jsonld[0]
    assert '"isAccessibleForFree": "False"' in jsonld.text


def test_abo_paywall_schema_attr_not_on_free_content(testbrowser):
    browser = testbrowser('/zeit-online/article/simple')
    jsonld = browser.cssselect('script[type="application/ld+json"]')
    assert len(jsonld) == 0


def test_dpa_article_should_have_correct_header(testbrowser):
    browser = testbrowser('/zeit-online/article/dpa')
    assert len(browser.cssselect('.dpa-header')) == 1

    browser = testbrowser('/zeit-online/article/dpa-image')
    assert len(browser.cssselect('.dpa-header')) == 1
    assert len(browser.cssselect('.dpa-header__image')) == 1


def test_font_sizing_via_js_api_from_app(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-online/slenderized-index' % testserver.url)
    html_elem = driver.find_element_by_css_selector('html')

    driver.execute_script("window.Zeit.setFontSize(0)")
    assert not html_elem.get_attribute('style')

    driver.execute_script("window.Zeit.setFontSize('Wurstbrot')")
    assert not html_elem.get_attribute('style')

    driver.execute_script("window.Zeit.setFontSize(200)")
    assert html_elem.get_attribute('style') == 'font-size: 200%;'

    driver.get('%s/zeit-online/article/simple' % testserver.url)
    condition = expected_conditions.visibility_of_element_located((
        By.CSS_SELECTOR, '.main--article'))
    assert WebDriverWait(selenium_driver, 1).until(condition)

    html_elem = driver.find_element_by_css_selector('html')
    assert html_elem.get_attribute('style') == 'font-size: 200%;'

    # clean up to not harm the next tests
    driver.execute_script("window.localStorage.clear()")


def test_dpa_noimage_article_renders_empty_image_block(testbrowser):
    browser = testbrowser('/zeit-online/article/dpa')
    empty_img_block = browser.cssselect('.dpa-header__image:empty')
    assert len(empty_img_block) == 1


@pytest.mark.parametrize(
    'parameter', [
        ('dpa'),
        ('afp')
    ])
def test_dpa_afp_article_should_have_notice(testbrowser, parameter):
    browser = testbrowser('/zeit-online/article/' + parameter)
    assert len(browser.cssselect('.article-notice')) == 1
