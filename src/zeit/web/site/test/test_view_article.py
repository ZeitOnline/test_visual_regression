# -*- coding: utf-8 -*-
import base64
import mock
import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC  # NOQA
from selenium.webdriver.support.ui import WebDriverWait

import zeit.web.site.view_article
import zeit.cms.interfaces


screen_sizes = ((320, 480, True), (520, 960, True),
                (768, 1024, False), (980, 1024, False))


@pytest.fixture(scope='session', params=screen_sizes)
def screen_size(request):
    return request.param


def test_article_should_render_full_view(testserver, testbrowser):
    article_path = '{}/zeit-online/article/zeit{}'
    browser = testbrowser(article_path.format(
        testserver.url, '/komplettansicht'))
    article = zeit.cms.interfaces.ICMSContent(
        article_path.format('http://xml.zeit.de', ''))
    assert len(browser.cssselect(
        '.article-page > p.paragraph')) == article.paragraphs


def test_article_full_view_has_no_pagination(testbrowser, testserver):
    select = testbrowser('{}/zeit-online/article/zeit/komplettansicht'.format(
        testserver.url)).cssselect

    assert len(select('.summary, .byline, .metadata')) == 3
    assert len(select('.article-pagination')) == 0


def test_article_with_pagination(testbrowser, testserver):
    browser = testbrowser('{}/zeit-online/article/zeit'.format(testserver.url))
    select = browser.cssselect
    nexttitle = select('.article-pagination__nexttitle')
    numbers = select('.article-pager__number')

    assert len(select('.summary, .byline, .metadata')) == 3
    assert len(select('.article__page-teaser')) == 0
    assert len(select('.article-pagination')) == 1
    assert len(nexttitle) == 1
    assert nexttitle[0].text.strip() == (
        u'Der Horror von Crystal wurzelt in der Normalität')
    assert len(numbers) == 5
    assert '--current' in (numbers[0].get('class'))


def test_article_pagination_active_state(testbrowser, testserver):
    select = testbrowser('{}/zeit-online/article/zeit/seite-3'.format(
        testserver.url)).cssselect

    assert len(select('.summary, .byline, .metadata')) == 0
    assert select('.article__page-teaser')[0].text.strip() == (
        u'Seite 3/5: Man wird schlank und lüstern')
    assert select('.article-pagination__nexttitle')[0].text.strip() == (
        u'Aus dem abenteuerlustigen Mädchen vom Dorf wurde ein Junkie')
    assert '--current' in (select('.article-pager__number')[2].get('class'))


def test_breaking_news_article_renders_breaking_bar(testbrowser, testserver):
    select = testbrowser('{}/zeit-online/article/eilmeldungsartikel'.format(
        testserver.url)).cssselect

    assert len(select('.breaking-news-banner')) == 1
    assert len(select('.breaking-news-heading')) == 1


def test_schema_org_main_content_of_page(testbrowser, testserver):
    select = testbrowser('{}/zeit-online/article/01'.format(
        testserver.url)).cssselect

    assert len(select('main[itemprop="mainContentOfPage"]')) == 1


def test_schema_org_article(testbrowser, testserver):
    select = testbrowser('{}/zeit-online/article/01'.format(
        testserver.url)).cssselect

    assert len(select(
        'article[itemtype="http://schema.org/Article"][itemscope]')) == 1


def test_schema_org_headline(testbrowser, testserver):
    select = testbrowser('{}/zeit-online/article/01'.format(
        testserver.url)).cssselect
    headline = select('h1[itemprop="headline"]')
    text = u'"Der Hobbit": Geht\'s noch gr\xf6\xdfer?'
    assert len(headline) == 1
    assert text in headline[0].text_content()


def test_schema_org_description(testbrowser, testserver):
    select = testbrowser('{}/zeit-online/article/01'.format(
        testserver.url)).cssselect

    assert len(select('div[itemprop="description"]')) == 1


def test_schema_org_author(testbrowser, testserver):
    select = testbrowser('{}/zeit-online/article/01'.format(
        testserver.url)).cssselect

    assert len(select('.byline[itemprop="author"]')) == 1
    assert len(select('.byline a[itemprop="url"]')) == 1
    assert len(select('.byline span[itemprop="name"]')) == 1


def test_schema_org_article_body(testbrowser, testserver):
    select = testbrowser('{}/zeit-online/article/01'.format(
        testserver.url)).cssselect

    assert len(select('.article-body[itemprop="articleBody"]')) == 1


def test_schema_org_image(testbrowser, testserver):
    select = testbrowser('{}/zeit-online/article/01'.format(
        testserver.url)).cssselect
    json = 'article > script[type="application/ld+json"]'
    assert len(select(json)) == 1


def test_multipage_article_should_designate_meta_pagination(
        testbrowser, testserver):
    browser = testbrowser('{}/zeit-online/article/zeit'.format(
        testserver.url))
    assert not browser.xpath('//head/meta[@rel="prev"]')
    href = browser.xpath('//head/meta[@rel="next"]')[0].attrib.get('href')
    assert href.endswith('zeit-online/article/zeit/seite-2')

    browser = testbrowser('{}/zeit-online/article/zeit/seite-2'.format(
        testserver.url))
    href = browser.xpath('//head/meta[@rel="prev"]')[0].attrib.get('href')
    assert href.endswith('zeit-online/article/zeit')
    href = browser.xpath('//head/meta[@rel="next"]')[0].attrib.get('href')
    assert href.endswith('zeit-online/article/zeit/seite-3')

    browser = testbrowser('{}/zeit-online/article/zeit/seite-5'.format(
        testserver.url))
    href = browser.xpath('//head/meta[@rel="prev"]')[0].attrib.get('href')
    assert href.endswith('zeit-online/article/zeit/seite-4')
    assert not browser.xpath('//head/meta[@rel="next"]')


def test_other_page_types_should_not_designate_meta_pagination(
        testbrowser, testserver):
    browser = testbrowser('{}/zeit-online/article/01'.format(testserver.url))
    assert not browser.xpath('//head/meta[@rel="prev"]')
    assert not browser.xpath('//head/meta[@rel="next"]')

    browser = testbrowser('{}/zeit-online/index'.format(testserver.url))
    assert not browser.xpath('//head/meta[@rel="prev"]')
    assert not browser.xpath('//head/meta[@rel="next"]')


def test_article_obfuscated_source_without_date_print_published():
    content = mock.Mock()
    content.product.label = content.product.title = 'DIE ZEIT'
    content.product.show = 'issue'
    content.volume = 1
    content.year = 2011
    view = zeit.web.site.view_article.Article(content, mock.Mock())
    view.date_print_published = None
    source = u'DIE ZEIT N\u00B0\u00A01/2011'
    assert view.obfuscated_source == base64.b64encode(source.encode('latin-1'))


def test_article_sharing_menu_should_open_and_close(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.set_window_size(320, 480)
    driver.get('%s/zeit-online/article/01' % testserver.url)

    sharing_menu_selector = '.sharing-menu > .sharing-menu__items'
    sharing_menu_target = driver.find_element_by_css_selector(
        '.sharing-menu > .sharing-menu__title.js-sharing-menu')
    sharing_menu_items = driver.find_element_by_css_selector(
        sharing_menu_selector)

    assert sharing_menu_items.is_displayed() is False, (
        'sharing menu should be hidden by default')

    sharing_menu_target.click()
    assert sharing_menu_items.is_displayed(), (
        'sharing menu should be visible after interaction')

    sharing_menu_target.click()
    # we need to wait for the CSS animation to finish
    # so the sharing menu is actually hidden
    condition = EC.invisibility_of_element_located((
        By.CSS_SELECTOR, sharing_menu_selector))
    assert WebDriverWait(driver, 1).until(condition), (
        'sharing menu should hide again on click')


def test_article_sharing_menu_should_hide_whatsapp_link_tablet_upwards(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.set_window_size(768, 800)
    driver.get('%s/zeit-online/article/01' % testserver.url)

    sharing_menu_target = driver.find_element_by_css_selector(
        '.sharing-menu > .sharing-menu__title.js-sharing-menu')
    whatsapp_item = driver.find_element_by_css_selector(
        '.sharing-menu__item--whatsapp')

    sharing_menu_target.click()
    assert not(whatsapp_item.is_displayed()), (
        'Sharing link to WhatsApp should be hidden on tablet & desktop')


def test_infobox_in_article_is_shown(testbrowser, testserver):
    select = testbrowser('{}/zeit-online/article/infoboxartikel'.format(
        testserver.url)).cssselect
    assert len(select('aside#sauriersindsuper.infobox')) == 1
    assert len(select('#sauriersindsuper label')) == 12
    assert len(select('#sauriersindsuper input[type="checkbox"]')) == 6
    assert len(select('#sauriersindsuper input[type="radio"]')) == 6


def test_infobox_interactions(selenium_driver, testserver, screen_size):
    driver = selenium_driver
    driver.set_window_size(screen_size[0], screen_size[1])
    driver.get('%s/zeit-online/article/infoboxartikel' % testserver.url)
    infobox = driver.find_element_by_id('sauriersindsuper')
    tabnavigation = infobox.find_elements_by_class_name(
        'infobox__navigation')[0]
    tabpanels = infobox.find_elements_by_class_name('infobox__inner')
    tabnavs = infobox.find_elements_by_class_name('infobox__navlabel')
    tabchecks = infobox.find_elements_by_class_name('infobox__label')

    assert infobox.is_displayed(), 'Infobox missing'
    if screen_size[0] == 320 or screen_size[0] == 520:
        assert not tabnavigation.is_displayed(), 'Mobile not accordion'
        tabchecks[1].click()
        assert tabpanels[1].get_attribute('aria-hidden') == 'false'
        tabchecks[2].click()
        assert tabpanels[1].get_attribute('aria-hidden') == 'false'
        assert tabpanels[2].get_attribute('aria-hidden') == 'false'
        tabchecks[1].click()
        assert tabpanels[1].get_attribute('aria-hidden') == 'true'
        assert tabpanels[2].get_attribute('aria-hidden') == 'false'
    if screen_size[0] > 767:
        assert tabnavigation.is_displayed(), 'Desktop not Tabs'
        tabnavs[3].click()
        assert tabpanels[1].get_attribute('aria-hidden') == 'true'
        assert tabpanels[2].get_attribute('aria-hidden') == 'true'
        assert tabpanels[3].get_attribute('aria-hidden') == 'false'


def test_article_has_news_source_as_list():
    content = mock.Mock()
    content.copyrights = 'ZEIT ONLINE, Reuters'

    view = zeit.web.site.view_article.Article(content, mock.Mock())
    assert view.news_source == 'ZEITONLINE;Reuters'


def test_article_has_news_source_dpa():
    content = mock.Mock()
    content.ressort = 'News'
    content.product.id = 'News'
    view = zeit.web.site.view_article.Article(content, mock.Mock())
    assert view.news_source == "dpa"


def test_article_has_news_source_sid():
    content = mock.Mock()
    content.product.id = 'SID'
    view = zeit.web.site.view_article.Article(content, mock.Mock())
    assert view.news_source == "Sport-Informations-Dienst"


def test_article_has_news_source_empty():
    content = mock.Mock()
    content.copyrights = None

    view = zeit.web.site.view_article.Article(content, mock.Mock())
    assert view.news_source == ''


def test_adcontroller_values_return_values_on_article(application):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/infoboxartikel')
    adcv = [
        ('$handle', 'artikel'),
        ('level2', u'wissen'),
        ('level3', 'umwelt'),
        ('$autoSizeFrames', True),
        ('keywords', ''),
        ('tma', '')]
    view = view = zeit.web.site.view_article.Article(content, mock.Mock())
    assert adcv == view.adcontroller_values
