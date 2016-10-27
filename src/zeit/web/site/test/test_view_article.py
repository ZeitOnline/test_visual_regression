# -*- coding: utf-8 -*-
import base64
import datetime
import urlparse

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
import lxml.etree
import mock
import pyramid.testing
import pytest
import re
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
                (768, 1024, False), (980, 1024, False))


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
    link = select('.article-pagination__link')[0].attrib['href']
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
    assert person.text == u'© Warner Bros.'

    assert date_published.get('datetime') == '2015-05-27T19:11:30+02:00'

    assert author.get('itemtype') == 'http://schema.org/Person'
    assert author.cssselect('[itemprop="name"]')[0].text == 'Wenke Husmann'
    assert author.cssselect('[itemprop="url"]')[0].get('href') == (
        'http://localhost/autoren/H/Wenke_Husmann/index.xml')


def test_multipage_article_should_designate_meta_pagination(testbrowser):
    browser = testbrowser('/zeit-online/article/zeit')
    assert not browser.xpath('//head/link[@rel="prev"]')
    href = browser.xpath('//head/link[@rel="next"]')[0].attrib.get('href')
    assert href.endswith('zeit-online/article/zeit/seite-2')

    browser = testbrowser('/zeit-online/article/zeit/seite-2')
    href = browser.xpath('//head/link[@rel="prev"]')[0].attrib.get('href')
    assert href.endswith('zeit-online/article/zeit')
    href = browser.xpath('//head/link[@rel="next"]')[0].attrib.get('href')
    assert href.endswith('zeit-online/article/zeit/seite-3')

    browser = testbrowser('/zeit-online/article/zeit/seite-5')
    href = browser.xpath('//head/link[@rel="prev"]')[0].attrib.get('href')
    assert href.endswith('zeit-online/article/zeit/seite-4')
    assert not browser.xpath('//head/link[@rel="next"]')


def test_other_page_types_should_not_designate_meta_pagination(testbrowser):
    browser = testbrowser('/zeit-online/article/01')
    assert not browser.xpath('//head/link[@rel="prev"]')
    assert not browser.xpath('//head/link[@rel="next"]')

    browser = testbrowser('/zeit-online/index')
    assert not browser.xpath('//head/link[@rel="prev"]')
    assert not browser.xpath('//head/link[@rel="next"]')


def test_article_obfuscated_source_without_date_print_published():
    content = mock.Mock()
    content.product.label = content.product.title = 'DIE ZEIT'
    content.product.show = 'issue'
    content.copyrights = ''
    content.volume = 1
    content.year = 2011
    view = zeit.web.site.view_article.Article(
        content, pyramid.testing.DummyRequest())
    view.date_print_published = None
    source = u'DIE ZEIT Nr.\u00A01/2011'
    assert view.obfuscated_source == base64.b64encode(source.encode('latin-1'))


def test_article_sharing_menu_should_open_and_close(
        testserver, selenium_driver):
    selenium_driver.set_window_size(320, 480)
    selenium_driver.get('{}/zeit-online/article/01'.format(testserver.url))

    sharing_menu_selector = '.sharing-menu > .sharing-menu__items'
    sharing_menu_target = selenium_driver.find_element_by_css_selector(
        '.sharing-menu > a[aria-controls]')
    sharing_menu_items = selenium_driver.find_element_by_css_selector(
        sharing_menu_selector)

    assert sharing_menu_items.is_displayed() is False, (
        'sharing menu should be hidden by default')

    sharing_menu_target.click()
    # we need to wait for the CSS animation to finish
    # so the sharing menu is actually visible
    condition = expected_conditions.visibility_of_element_located((
        By.CSS_SELECTOR, sharing_menu_selector))
    assert WebDriverWait(
        selenium_driver, 1).until(condition), (
            'sharing menu should be visible after interaction')

    sharing_menu_target.click()
    # we need to wait for the CSS animation to finish
    # so the sharing menu is actually hidden
    condition = expected_conditions.invisibility_of_element_located((
        By.CSS_SELECTOR, sharing_menu_selector))
    assert WebDriverWait(
        selenium_driver, 1).until(condition), (
            'sharing menu should hide again on click')


def test_article_sharing_menu_should_hide_whatsapp_link_tablet_upwards(
        testserver, selenium_driver):
    selenium_driver.set_window_size(768, 800)
    selenium_driver.get('{}/zeit-online/article/01'.format(testserver.url))

    sharing_menu_target = selenium_driver.find_element_by_css_selector(
        '.sharing-menu > a[aria-controls]')
    whatsapp_item = selenium_driver.find_element_by_css_selector(
        '.sharing-menu__item--whatsapp')

    sharing_menu_target.click()
    assert not(whatsapp_item.is_displayed()), (
        'Sharing link to WhatsApp should be hidden on tablet & desktop')


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


def test_adcontroller_values_return_values_on_article(application):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/infoboxartikel')
    adcv = [
        ('$handle', 'artikel'),
        ('level2', u'wissen'),
        ('level3', 'umwelt'),
        ('level4', ''),
        ('$autoSizeFrames', True),
        ('keywords', 'zeitonline'),
        ('tma', '')]
    view = view = zeit.web.site.view_article.Article(
        content, pyramid.testing.DummyRequest())
    assert adcv == view.adcontroller_values


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

    if screen_size[0] == 980:
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


def test_article_for_column_without_authorimage_should_be_rendered_default(
        testbrowser):
    browser = testbrowser('/zeit-online/cp-content/kolumne-ohne-autorenbild')

    assert len(browser.cssselect('.article--columnarticle')) == 0
    assert len(browser.cssselect('.column-heading')) == 0


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


def test_breaking_news_banner_shows_date_first_released(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/breaking_news.tpl')
    view = mock.Mock()
    view.breaking_news.published = True
    view.breaking_news.date_first_released = datetime.time(11, 55, 0)
    html_str = tpl.render(view=view)
    html = lxml.html.fromstring(html_str)
    time = html.cssselect('.breaking-news-banner__time')
    assert time[0].text == '11:55 Uhr'


def test_tile7_is_rendered_on_articles_with_multiple_pages(testbrowser):
    selector = ('#ad-desktop-7', '#ad-mobile-4')

    browser = testbrowser('/zeit-online/article/zeit')
    assert len(browser.cssselect(selector[0])) == 1
    assert len(browser.cssselect(selector[1])) == 1

    browser = testbrowser('/zeit-online/article/zeit/seite-2')
    assert len(browser.cssselect(selector[0])) == 1
    assert len(browser.cssselect(selector[1])) == 1

    browser = testbrowser('/zeit-online/article/zeit/seite-5')
    assert len(browser.cssselect(selector[0])) == 1
    assert len(browser.cssselect(selector[1])) == 1


def test_tiles7_9_are_rendered_on_articles_with_multiple_pages_on_onepage_view(
        testbrowser):
    browser = testbrowser('/zeit-online/article/zeit/komplettansicht')
    assert len(browser.cssselect('#ad-desktop-7')) == 1
    assert len(browser.cssselect('#ad-mobile-4')) == 1
    assert len(browser.cssselect('#ad-desktop-9')) == 1


def test_article_ads_should_have_pagetype_modifier(testbrowser):
    browser = testbrowser('/zeit-online/article/01')
    assert len(browser.cssselect('#ad-desktop-7')) == 1
    assert 'ad-desktop--7-on-article' in browser.contents


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
    assert view.meta_robots == 'noindex,follow,noodp,noydir,noarchive'


def test_tgs_article_has_correct_meta_robots(
        application, monkeypatch, dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    monkeypatch.setattr(
        zeit.web.site.view_article.Article, u'product_id', u'TGS')
    view = zeit.web.site.view_article.Article(context, dummy_request)
    assert view.meta_robots == 'noindex,follow,noodp,noydir,noarchive'


def test_habl_article_has_correct_meta_robots(
        application, monkeypatch, dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    monkeypatch.setattr(
        zeit.web.site.view_article.Article, u'product_id', u'HaBl')
    view = zeit.web.site.view_article.Article(context, dummy_request)
    assert view.meta_robots == 'noindex,follow,noodp,noydir,noarchive'


def test_wiwo_article_has_correct_meta_robots(
        application, monkeypatch, dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    monkeypatch.setattr(
        zeit.web.site.view_article.Article, u'product_id', u'WIWO')
    view = zeit.web.site.view_article.Article(context, dummy_request)
    assert view.meta_robots == 'noindex,follow,noodp,noydir,noarchive'


def test_golem_article_has_correct_meta_robots(
        application, monkeypatch, dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    monkeypatch.setattr(
        zeit.web.site.view_article.Article, u'product_id', u'GOLEM')
    view = zeit.web.site.view_article.Article(context, dummy_request)
    assert view.meta_robots == 'noindex,follow,noodp,noydir,noarchive'


def test_sharing_cardstack_article_has_correct_meta_robots(
        application, monkeypatch, dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    monkeypatch.setattr(
        zeit.web.site.view_article.Article, u'shared_cardstack_id', u'kekse')
    view = zeit.web.site.view_article.Article(context, dummy_request)
    assert view.meta_robots == 'noindex,follow,noodp,noydir,noarchive'


def test_zei_article_has_correct_meta_robots(
        application, monkeypatch, dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    monkeypatch.setattr(
        zeit.web.site.view_article.Article, u'product_id', u'ZEI')
    view = zeit.web.site.view_article.Article(context, dummy_request)
    assert view.meta_robots == 'index,follow,noodp,noydir,noarchive'


def test_unset_product_id_article_has_correct_meta_robots(
        application, monkeypatch, dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    monkeypatch.setattr(
        zeit.web.site.view_article.Article, u'product_id', None)
    view = zeit.web.site.view_article.Article(context, dummy_request)
    assert view.meta_robots == 'index,follow,noodp,noydir,noarchive'


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
    assert view.meta_robots == 'index,nofollow,noodp,noydir,noarchive', (
        'wrong robots for usual angebot')

    # partnersuche
    request.path = '/angebote/partnersuche/test'
    view = zeit.web.site.view_article.Article(article, request)
    assert view.meta_robots == 'index,follow,noodp,noydir,noarchive', (
        'wrong robots for partnersuche')


def test_robots_rules_for_diverse_articles(application):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    request = pyramid.testing.DummyRequest()
    request.url = 'http://localhost'

    # test folder
    request.path = '/test/article'
    view = zeit.web.site.view_article.Article(article, request)
    assert view.meta_robots == 'noindex,follow,noodp,noydir,noarchive', (
        'wrong robots for test folder')

    # templates folder
    request.path = '/templates/article'
    view = zeit.web.site.view_article.Article(article, request)
    assert view.meta_robots == 'noindex,follow,noodp,noydir,noarchive', (
        'wrong robots for templates folder')

    # banner folder
    request.path = '/banner/article'
    view = zeit.web.site.view_article.Article(article, request)
    assert view.meta_robots == 'noindex,follow,noodp,noydir,noarchive', (
        'wrong robots for banner folder')

    # any folder
    request.path = '/any/article'
    view = zeit.web.site.view_article.Article(article, request)
    assert view.meta_robots == 'index,follow,noodp,noydir,noarchive', (
        'wrong robots for any other folder')


def test_article_doesnt_show_modified_date(testbrowser):
    select = testbrowser('/zeit-online/article/01').cssselect
    date_string = select('.metadata__date')[0].text.strip()
    assert date_string == '27. Mai 2015, 19:11 Uhr'


def test_video_in_article_is_there(testbrowser):
    article = testbrowser('/zeit-online/article/zeit')
    assert len(article.cssselect('.video-player__videotag')) == 1


def test_advertorial_marker_is_present(testbrowser):
    browser = testbrowser('zeit-online/article/angebot')
    assert len(browser.cssselect('.advertorial-marker')) == 1
    assert len(browser.cssselect('.advertorial-marker__title')) == 1
    assert len(browser.cssselect('.advertorial-marker__text')) == 1
    assert len(browser.cssselect('.advertorial-marker__label')) == 1


def test_canonical_url_should_omit_queries_and_hashes(testbrowser):
    browser = testbrowser('/zeit-online/article/zeit/seite-3?cid=123#comments')
    canonical_url = browser.cssselect('link[rel=canonical]')[0].attrib['href']
    assert canonical_url.endswith('zeit-online/article/zeit/seite-3')


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
    assert keyword.attrib['href'].endswith('/thema/wein')


def test_article_has_print_pdf_function(testbrowser):
    browser = testbrowser('/zeit-online/article/01')
    links = browser.cssselect('.print-menu__link')
    assert (links[0].attrib['href'].endswith(
        '/zeit-online/article/01?print'))
    assert (links[1].attrib['href'] ==
            'http://pdf.zeit.de/zeit-online/article/01.pdf')


def test_multi_page_article_has_print_link(testbrowser):
    browser = testbrowser('/zeit-online/article/tagesspiegel')
    links = browser.cssselect('.print-menu__link')
    assert (links[0].attrib['href'].endswith(
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


def test_article_lineage_should_render_correctly(testbrowser):
    browser = testbrowser('/zeit-online/article/zeit')
    assert len(browser.cssselect('.al-text--prev')) == 1
    assert len(browser.cssselect('.al-text--next')) == 1


def test_article_lineage_should_utilize_feature_toggle(
        testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'article_lineage': False}.get)
    browser = testbrowser('/zeit-online/article/zeit')
    assert len(browser.cssselect('.article-lineage')) == 0


def test_article_lineage_has_text_elements(testbrowser):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{
        u'supertitle': u'a',
        u'uniqueId': u'http://xml.zeit.de/01',
        u'title': u'b'}, {
            u'supertitle': u'c',
            u'uniqueId': u'http://xml.zeit.de/02',
            u'title': u'd'}]
    browser = testbrowser('/zeit-online/article/zeit')
    assert len(browser.cssselect('.al-text__kicker')) == 2
    assert len(browser.cssselect('.al-text__supertitle')) == 2
    assert len(browser.cssselect('.al-text__title')) == 2


@pytest.mark.xfail(reason='This test fails on Jenkins. Disabled until fixed.')
def test_article_lineage_should_be_hidden_on_small_screens(
        selenium_driver, testserver, screen_size):
    driver = selenium_driver
    driver.set_window_size(screen_size[0], screen_size[1])
    driver.get('%s/zeit-online/article/zeit' % testserver.url)
    driver.execute_script("window.scrollTo(0, 500)")
    lineage_links = driver.find_elements_by_css_selector(
        '.al-link')
    lineage_linktexts = driver.find_elements_by_css_selector(
        '.al-text')

    if screen_size[0] < 980:
        assert not lineage_links[0].is_displayed()
        assert not lineage_links[1].is_displayed()
        assert not lineage_linktexts[0].is_displayed()
        assert not lineage_linktexts[1].is_displayed()

    if screen_size[0] >= 980:
        assert lineage_links[0].is_displayed()
        assert lineage_links[1].is_displayed()
        assert not lineage_linktexts[0].is_displayed()
        assert not lineage_linktexts[1].is_displayed()


@pytest.mark.xfail(reason='This test fails on Jenkins. Disabled until fixed.')
def test_article_lineage_should_be_fixed_after_scrolling(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.set_window_size(980, 1024)
    driver.get('%s/zeit-online/article/zeit' % testserver.url)
    driver.execute_script("window.scrollTo(0, 1200)")
    try:
        wait = WebDriverWait(driver, 10)
        wait.until(expected_conditions.visibility_of_element_located(
                   (By.CSS_SELECTOR, '.article-lineage--fixed')))
    except TimeoutException:
        assert False, 'Fixed Lineage not visible after scrolled into view'


@pytest.mark.xfail(reason='This test fails on Jenkins. Disabled until fixed.')
def test_article_lineage_overlapping_with_fullwidth_elements_should_be_hidden(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.set_window_size(1024, 768)
    driver.get('%s/zeit-online/article/infoboxartikel' % testserver.url)
    # Force page load even if another test has left the browser on _this_ page.
    driver.refresh()

    driver.execute_script('window.scrollTo(0, 600)')
    wait = WebDriverWait(driver, 5)

    try:
        wait.until(expected_conditions.visibility_of_element_located(
                   (By.CSS_SELECTOR, '.article-lineage')))
    except TimeoutException:
        assert False, 'Fixed Lineage not visible after scrolled into view'

    driver.get('%s/zeit-online/article/infoboxartikel#info-bonobo' %
               testserver.url)

    try:
        wait.until(expected_conditions.invisibility_of_element_located(
                   (By.CSS_SELECTOR, '.article-lineage')))
    except TimeoutException:
        assert False, 'Fixed Lineage visible above fullwidth element'


def test_article_lineage_should_not_render_on_advertorials(testbrowser):
    browser = testbrowser('/zeit-online/article/angebot')
    assert len(browser.cssselect('.article-lineage')) == 0


def test_article_lineage_should_not_render_on_articles_without_channels(
        testbrowser):
    browser = testbrowser('/zeit-online/article/dpa')
    assert len(browser.cssselect('.article-lineage')) == 0


def test_article_lineage_should_not_render_on_administratives(testbrowser):
    browser = testbrowser('/zeit-online/article/administratives')
    assert len(browser.cssselect('.article-lineage')) == 0


def test_advertisement_nextread_should_render_after_veeseo(
        testbrowser, workingcopy):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    with checked_out(article) as co:
        co.ressort = u'Wirtschaft'
        co.sub_ressort = None
        zeit.cms.related.interfaces.IRelatedContent(co).related = (
            zeit.cms.interfaces.ICMSContent(
                'http://xml.zeit.de/zeit-online/article/02'),)
    browser = testbrowser('/zeit-online/article/01')
    nextread = browser.xpath('//main/article')[1]
    veeseo = browser.xpath('//main/div')[1]
    ad = browser.xpath('//main/article')[2]
    assert nextread.attrib.get('class') == 'nextread nextread--with-image'
    assert veeseo.attrib.get('class') == 'RA2VW2'
    assert ad.attrib.get('class') == 'nextread-advertisement'


def test_article_should_contain_veeseo_widget(testbrowser):
    select = testbrowser('/zeit-online/article/01').cssselect
    assert select('script[src="http://rce.veeseo.com/widgets/zeit/widget.js"]')
    assert select('.RA2VW2')


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

    canonical = bro.cssselect('link[rel=canonical]')[0].attrib['href']
    assert 'zeit-online/article/quotes' in canonical
    assert 'instantarticle' not in canonical
    assert '"Pulp Fiction"' in bro.cssselect('h1')[0].text
    assert bro.cssselect('.op-published')[0].text.strip() == '2. Juni 1999'
    assert bro.cssselect('.op-modified')[0].text.strip() == '20. Dezember 2013'
    assert bro.cssselect('figure > img[src$="square__2048x2048"]')
    assert len(bro.cssselect('aside')) == 3
    assert 'Bernie Sanders' in bro.cssselect('figcaption')[0].text
    assert u'© Warner Bros.' == bro.cssselect('figcaption > cite')[0].text


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
    assert browser.cssselect('address a')[0].attrib.get('href').endswith(
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
    browser = testbrowser(
        '/instantarticle/zeit-online/article/simple-multipage')
    assert len(browser.cssselect(
        'iframe[src$="/static/latest/html/fbia-ads/tile-4.html"]')) == 1
    assert len(browser.cssselect(
        'iframe[src$="/static/latest/html/fbia-ads/tile-5.html"]')) == 1
    assert len(browser.cssselect(
        'iframe[src$="/static/latest/html/fbia-ads/tile-8.html"]')) == 1


def test_instantarticle_shows_ad_after_100_words(testbrowser):
    word_count = 0
    bro = testbrowser('/instantarticle/zeit-online/article/simple-multipage')
    blocks = bro.xpath('body/article/*')
    blocks = blocks[1:]
    for block in blocks:
        if block.tag == 'p':
            words = len(re.findall(r'\S+', block.text_content()))
            word_count = word_count + words
        if block.tag == 'figure':
            assert block.cssselect('iframe[src*="tile-4"]')
            break
    assert word_count > 100


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
    browser = testbrowser('/zeit-online/article/simple')
    counter = browser.cssselect('body noscript img[src^="http://cc.zeit.de"]')
    assert ("img.src = 'http://cc.zeit.de/cc.gif?banner-channel="
            "sport/article") in browser.contents
    assert len(counter) == 1
    assert ('cc.zeit.de/cc.gif?banner-channel=sport/article'
            ) in counter[0].get('src')


def test_fbia_article_contains_meta_robots(testbrowser):
    browser = testbrowser('/fbia/zeit-online/article/simple')
    assert '<meta name="robots" content="noindex, follow">' in browser.contents


def test_fbia_article_contains_correct_webtrekk_platform(testbrowser):
    browser = testbrowser('/fbia/zeit-online/article/simple')
    assert '25: "instant article"' in browser.contents


def test_amp_link_should_be_present_and_link_to_the_correct_amp(testbrowser):
    browser = testbrowser('/zeit-online/article/zeit')
    amp_link = browser.cssselect('link[rel=amphtml]')
    assert amp_link
    amp_url = amp_link[0].attrib['href']
    assert amp_url.endswith('amp/zeit-online/article/zeit')

    browser = testbrowser('/zeit-online/article/zeit/seite-2')
    amp_link = browser.cssselect('link[rel=amphtml]')
    assert amp_link
    amp_url = amp_link[0].attrib['href']
    assert amp_url.endswith('amp/zeit-online/article/zeit')


def test_newsletter_optin_page_has_webtrekk_ecommerce(testbrowser):
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


def test_advertorial_article_contains_correct_webtrekk_param(dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/angebot')
    view = zeit.web.site.view_article.Article(context, dummy_request)
    assert view.webtrekk['customParameter']['cp26'] == 'article.advertorial'


def test_serie_article_contains_correct_webtrekk_param(dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    view = zeit.web.site.view_article.Article(context, dummy_request)
    assert view.webtrekk['customParameter']['cp26'] == 'article.serie'


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

    url = browser.cssselect('.article-series__heading')[0].attrib['href']
    assert url.endswith('/serie/70-jahre-zeit')

    browser = testbrowser('/zeit-online/article/02')

    url = browser.cssselect('.article-series__heading')[0].attrib['href']
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
    image.copyrights = ('FOO', 'BAR', 'BAZ')
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
    image.copyrights = ()
    browser = tplbrowser(template, block=image, request=dummy_request)
    assert browser.cssselect('.infographic__caption')

    image.origin = False
    image.copyrights = ('FOO', 'BAR', 'BAZ')
    browser = tplbrowser(template, block=image, request=dummy_request)
    assert browser.cssselect('.infographic__caption')

    # no border styles present
    image.copyrights = ()
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

    browser = testbrowser('/zeit-online/article/infoboxartikel')
    assert len(browser.cssselect(selector)) == 1

    browser = testbrowser('/zeit-online/article/zeit')
    assert len(browser.cssselect(selector)) == 1

    browser = testbrowser('/zeit-online/article/zeit/seite-3')
    assert len(browser.cssselect(selector)) == 1

    browser = testbrowser('/zeit-online/article/zeit/komplettansicht')
    assert len(browser.cssselect(selector)) == 1


def test_zplus_badge_should_be_rendered_on_nextread(testbrowser):
    browser = testbrowser('/zeit-online/article/simple-nextread-zplus')

    zplus_badge = browser.cssselect('.nextread__kicker-logo--zplus')
    assert len(zplus_badge) == 1

    link = browser.cssselect('.nextread__link')
    assert len(link) == 1
    data_id = link[0].attrib['data-id']
    assert data_id == 'articlebottom.editorial-nextread...area-zplus'


def test_article_byline_is_displayed_completely(testbrowser):
    browser = testbrowser('/zeit-online/article/01')
    dom_node_byline = browser.cssselect('.byline')
    assert len(dom_node_byline) == 1
    raw_inner_html = dom_node_byline[0].text_content().replace("\n", "")
    assert " ".join(raw_inner_html.split()) == \
           'Eine Glosse von Wenke Husmann, Jochen Bittner,' \
           ' Heike Jahberg und Jasper Riemann'


def test_video_in_article_has_poster_copyright(testbrowser):
    browser = testbrowser('/zeit-online/article/zeit')
    figure_copyright_elem = browser.cssselect('.video-figure__copyright')
    assert len(figure_copyright_elem) == 1
    figure_copyright = figure_copyright_elem[0]
    copyright_person = figure_copyright.cssselect('[itemprop="name"]')[0]
    assert copyright_person.text == u'© Foto: Alaa Al-Marjani/Reuters'


def test_zplus_zon_article_has_correct_markup(testbrowser):
    browser = testbrowser('/zeit-online/article/zplus-zon')

    zplus_box = browser.cssselect('.zplus--coverless')
    assert len(zplus_box) == 1

    zplus_banner = zplus_box[0].cssselect('.zplus__banner')
    zplus_marker = zplus_box[0].cssselect('.zplus__marker')
    zplus_text = zplus_box[0].cssselect('.zplus__text')
    zplus_link = zplus_box[0].cssselect('.zplus__link')
    zplus_modifier = browser.cssselect('.article__item--has-badge')

    assert len(zplus_modifier) == 2
    assert len(zplus_banner) == 1
    assert len(zplus_marker) == 1
    assert len(zplus_text) == 1
    assert len(zplus_link) == 1
    assert 'exklusiv' in zplus_box[0].cssselect('a')[0].attrib['href']
    assert 'Exklusiv' in zplus_link[0].text.strip()


def test_zplus_volumeless_print_article_has_zplus_zon_badge(testbrowser):
    browser = testbrowser('/zeit-online/article/zplus-novolume')

    zplus_box = browser.cssselect('.zplus--coverless')
    assert len(zplus_box) == 1

    zplus_banner = zplus_box[0].cssselect('.zplus__banner')
    zplus_badge = zplus_box[0].cssselect('.zplus__marker')
    zplus_modifier = browser.cssselect('.article__item--has-badge')

    assert len(zplus_modifier) == 2
    assert len(zplus_banner) == 1
    assert len(zplus_badge) == 1


def test_zplus_abo_print_article_has_correct_markup(testbrowser):
    browser = testbrowser('/zeit-online/article/zplus-zeit')

    zplus_box = browser.cssselect('.zplus')
    assert len(zplus_box) == 1

    zplus_banner = zplus_box[0].cssselect('.zplus__banner')
    zplus_marker = zplus_box[0].cssselect('.zplus__marker')
    zplus_text = zplus_box[0].cssselect('.zplus__text')
    zplus_cover = zplus_box[0].cssselect('.zplus__media')
    zplus_media = zplus_box[0].cssselect('.zplus__media-item')
    zplus_link = zplus_box[0].cssselect('.zplus__link')
    zplus_modifier = browser.cssselect('.article__item--has-badge')

    assert len(zplus_modifier) == 2
    assert len(zplus_banner) == 1
    assert len(zplus_marker) == 1
    assert len(zplus_text) == 1
    assert len(zplus_cover) == 1
    assert len(zplus_media) == 1
    assert len(zplus_link) == 1
    assert '/2014/49' in zplus_box[0].cssselect('a')[0].attrib['href']
    assert 'Exklusiv' in zplus_link[0].text.strip()
    assert ('/angebote/printkiosk/bildergruppen/die-zeit-cover/'
            in zplus_media[0].attrib['src'])


def test_zplus_print_article_has_correct_markup(
        testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'reader_revenue': True}.get)
    browser = testbrowser('/zeit-online/article/zplus-zeit-register')

    zplus_box = browser.cssselect('.zplus')
    assert len(zplus_box) == 1

    article_metadata_source = browser.cssselect('.metadata__source')
    zplus_banner = zplus_box[0].cssselect('.zplus__banner')
    zplus_marker = zplus_box[0].cssselect('.zplus__marker')
    zplus_text = zplus_box[0].cssselect('.zplus__text')
    zplus_cover = zplus_box[0].cssselect('.zplus__media')
    zplus_media = zplus_box[0].cssselect('.zplus__media-item')
    zplus_link = zplus_box[0].cssselect('.zplus__link')
    zplus_label = zplus_box[0].cssselect('.zplus__label')
    zplus_modifier = browser.cssselect('.article__item--has-badge')

    assert len(zplus_modifier) == 2
    assert len(zplus_banner) == 1
    assert len(zplus_marker) == 0
    assert len(zplus_text) == 1
    assert len(zplus_cover) == 1
    assert len(zplus_media) == 1
    assert len(zplus_link) == 1
    assert len(zplus_label) == 1
    assert '/2014/49' in zplus_box[0].cssselect('a')[0].attrib['href']
    assert 'ZEIT Nr. 49/2014' in zplus_link[0].text.strip()
    assert 'Aus der' in zplus_label[0].text.strip()
    assert ('/angebote/printkiosk/bildergruppen/die-zeit-cover/'
            in zplus_media[0].attrib['src'])
    assert article_metadata_source.__len__() == 0


def test_zplus_print_article_has_correct_markup_if_reader_revenue_off(
        testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'reader_revenue': False}.get)
    browser = testbrowser('/zeit-online/article/zplus-zeit-register')

    article_metadata_source = browser.cssselect('.metadata__source')
    assert article_metadata_source.__len__() == 1


def test_free_print_article_has_volume_badge(testbrowser):
    browser = testbrowser('/zeit-online/article/zplus-zeit-free')
    badge = browser.cssselect('main article .zplus')[0]
    label = badge.cssselect('.zplus__text')[0]

    assert ' '.join(label.text_content().split()) == 'Aus der ZEIT Nr. 1/2016'
    assert badge.cssselect('.zplus__media')

    # test volume badge is in single page view too
    browser = testbrowser(
        '/zeit-online/article/zplus-zeit-free/komplettansicht')

    assert browser.cssselect('main article .zplus')


def test_free_print_article_shows_no_volume_badge_on_page_two(testbrowser):
    browser = testbrowser('/zeit-online/article/zplus-zeit-free/seite-2')

    assert not browser.cssselect('main article .zplus')


def test_registration_zon_article_has_no_zplus_badge(testbrowser):
    browser = testbrowser('/zeit-online/article/zplus-zon-register')

    assert not browser.cssselect('.zplus')
    assert not browser.cssselect('.article__item--has-badge')


def test_free_article_has_no_zplus_badge(testbrowser):
    browser = testbrowser('/zeit-online/article/simple')

    zplus_box = browser.cssselect('.zplus')
    zplus_modifier = browser.cssselect('.article__item--has-badge')

    assert len(zplus_box) == 0
    assert len(zplus_modifier) == 0


def test_volume_teaser_is_rendered_correctly(testbrowser):
    browser = testbrowser('/zeit-online/article/volumeteaser')
    volume_teaser = browser.cssselect('.volume-teaser')
    volume_teaser_link = browser.cssselect(
        '.volume-teaser__link')[0].get('href')
    assert len(volume_teaser) == 1
    assert volume_teaser_link == 'https://premium.zeit.de/diezeit/2016/' \
        '01?wt_zmc=fix.int.zonpme.zede.rr.premium_intern.packshot.' \
        'cover.cover&utm_medium=fix&utm_source=zede_zonpme_int&utm_campaign=' \
        'rr&utm_content=webreader_packshot_cover_cover'


def test_volume_teaser_display_correct_image_on_desktop(
        testserver, selenium_driver):
    selenium_driver.set_window_size(1280, 768)
    selenium_driver.get(
        '{}/zeit-online/article/volumeteaser'.format(testserver.url))
    img_src = selenium_driver.find_element_by_css_selector(
        '[data-src*="test-printcover"]').get_attribute('src')
    assert u'2016-09/test-printcover/original__220x158__desktop' in img_src


def test_share_buttons_are_present(testbrowser):
    browser = testbrowser('/zeit-online/article/simple')
    sharing_menu = browser.cssselect('.sharing-menu')[0]
    links = sharing_menu.cssselect('.sharing-menu__link')
    labels = sharing_menu.cssselect('.sharing-menu__text')

    assert 'sharing-menu--big' not in sharing_menu.attrib['class']

    #  facebook
    parts = urlparse.urlparse(links[0].attrib['href'])
    query = urlparse.parse_qs(parts.query)
    url = query.get('u').pop(0)
    assert 'wt_zmc=sm.ext.zonaudev.facebook.ref.zeitde.share_small.link' in url
    assert 'utm_medium=sm' in url
    assert 'utm_source=facebook_zonaudev_ext' in url
    assert 'utm_campaign=ref' in url
    assert 'utm_content=zeitde_share_small_link_x' in url

    #  twitter
    parts = urlparse.urlparse(links[1].attrib['href'])
    query = urlparse.parse_qs(parts.query)
    assert query.get('text').pop(0) == (
        'Williams wackelt weiter, steht aber im Viertelfinale')
    assert query.get('via').pop(0) == 'zeitonline'
    assert 'share_small' in query.get('url').pop(0)

    #  whatsapp
    parts = urlparse.urlparse(links[2].attrib['href'])
    query = urlparse.parse_qs(parts.query)
    assert ('Williams wackelt weiter, steht aber im Viertelfinale - '
            'Artikel auf ZEIT ONLINE: ') in query.get('text').pop(0)

    #  mail
    parts = urlparse.urlparse(links[3].attrib['href'])
    query = urlparse.parse_qs(parts.query)
    assert ('Williams wackelt weiter, steht aber im Viertelfinale - '
            'Artikel auf ZEIT ONLINE') in query.get('subject').pop(0)
    assert 'Artikel auf ZEIT ONLINE lesen:' in query.get('body').pop(0)

    assert labels[0].text == 'Facebook'
    assert labels[1].text == 'Twitter'
    assert labels[2].text == 'WhatsApp'
    assert labels[3].text == 'Mail'


def test_share_buttons_are_big(testbrowser):
    browser = testbrowser('/zeit-online/article/tags')
    sharing_menu = browser.cssselect('.sharing-menu2')[0]
    links = sharing_menu.cssselect('.sharing-menu2__link')
    labels = sharing_menu.cssselect('.sharing-menu2__text')

    assert 'sharing-menu2--big' in sharing_menu.attrib['class']
    assert len(links) == 4

    for link in links:
        assert '.ref.zeitde.share_big.' in link.attrib['href']

    assert labels[0].text == 'Auf Facebook teilen'
    assert labels[1].text == 'Twittern'
    assert labels[2].text == 'WhatsApp'
    assert labels[3].text == 'Mailen'


def test_article_view_has_share_buttons_set_correctly(
        application, dummy_request):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/simple')
    view = zeit.web.site.view_article.Article(article, dummy_request)
    assert not view.share_buttons
    assert view.webtrekk['customParameter']['cp31'] == 'share_buttons_small'

    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/tags')
    view = zeit.web.site.view_article.Article(article, dummy_request)
    assert view.share_buttons == 'big'
    assert view.webtrekk['customParameter']['cp31'] == 'share_buttons_big'


def test_merian_link_has_nofollow(testbrowser, dummy_request):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/simple-merian-nofollow')
    view = zeit.web.site.view_article.Article(article, dummy_request)
    assert view.product_id == 'merian'

    browser = testbrowser('/zeit-online/article/simple-merian-nofollow')
    sourcelink = browser.cssselect('.metadata__source a')[0]
    assert sourcelink.attrib['rel'] == 'nofollow'


def test_article_contains_authorbox(testbrowser):
    browser = testbrowser('/zeit-online/article/authorbox')
    authorbox = browser.cssselect('.authorbox')
    assert len(authorbox) == 3

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
