# -*- coding: utf-8 -*-
import pytest

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
import zeit.edit.interfaces
import zeit.content.article.edit
import zeit.cms.interfaces
import lxml.etree
import requests
import mock


def test_zar_article_single_page_has_no_pagination(testbrowser):
    select = testbrowser('/arbeit/article/simple').cssselect

    assert len(select('.summary, .byline, .metadata')) == 3
    assert len(select('.article-pagination')) == 1
    assert len(select('.article-pager')) == 0
    assert len(select('.article-toc')) == 0


def test_zar_article_full_view_has_no_pagination(testbrowser):
    select = testbrowser('/arbeit/article/paginated/komplettansicht').cssselect

    assert len(select('.summary, .byline, .metadata')) == 2
    assert len(select('.article-pagination')) == 1
    assert len(select('.article-pager')) == 0
    assert len(select('.article-toc')) == 0


def test_zar_article_paginated_has_toc(testbrowser):
    browser = testbrowser('/arbeit/article/paginated/')
    toc = browser.cssselect('.article-toc')
    assert len(toc) == 1


def test_zar_article_renders_quotes_correctly(testbrowser):
    browser = testbrowser('/arbeit/article/quotes')
    quotes = browser.cssselect('.quote')
    sources = browser.cssselect('.quote__source')
    assert len(quotes) == 4
    assert len(sources) == 2


@pytest.mark.parametrize('c1_parameter', [
    '?C1-Meter-Status=paywall&C1-Meter-User-Status=anonymous',
    '?C1-Meter-Status=paywall&C1-Meter-User-Status=registered',
    '?C1-Meter-Status=always_paid'])
def test_zar_paywall_switch_showing_forms(c1_parameter, testbrowser):
    urls = [
        'arbeit/article/paginated',
        'arbeit/article/paginated/seite-2',
        'arbeit/article/paginated/komplettansicht',
        'arbeit/article/simple'
    ]

    for url in urls:
        browser = testbrowser(
            '{}{}'.format(url, c1_parameter))
        assert len(browser.cssselect('.paragraph--faded')) == 1
        assert len(browser.cssselect('.gate')) == 1
        assert len(browser.cssselect(
            '.gate--register')) == int('anonymous' in c1_parameter)


def test_zar_article_zplus_comments_under_register_article(testbrowser):
    c1_param = '?C1-Meter-Status=paywall&C1-Meter-User-Status=anonymous'
    path = '/arbeit/article/comments'
    url = '{}{}'.format(path, c1_param)
    browser = testbrowser(url)

    assert len(browser.cssselect('.paragraph--faded')) == 1
    assert len(browser.cssselect('.gate')) == 1
    assert len(browser.cssselect('.comment-section')) == 1


def test_zar_article_zplus_comments_not_under_abo_article(testbrowser):
    c1_param = '?C1-Meter-Status=always_paid'
    path = '/arbeit/article/comments'
    url = '{}{}'.format(path, c1_param)
    browser = testbrowser(url)

    assert len(browser.cssselect('.comment-section')) == 0


def test_zar_article_paginated_has_headerimage_only_on_first_page(testbrowser):
    browser = testbrowser('/arbeit/article/01-digitale-nomaden/')
    assert len(browser.cssselect('.article__media--header-image')) == 1

    browser = testbrowser('/arbeit/article/01-digitale-nomaden/seite-2')
    assert not browser.cssselect('.article__media--header-image')

    browser = testbrowser(
        '/arbeit/article/01-digitale-nomaden/komplettansicht')
    assert len(browser.cssselect('.article__media--header-image')) == 1


def test_zar_article_image_has_caption(testbrowser):
    browser = testbrowser('/arbeit/article/01-digitale-nomaden')
    headerimage = browser.cssselect('figure.article__media--header-image')
    assert len(headerimage) == 1
    headerimage_caption = headerimage[0].cssselect('.figure__text')
    assert len(headerimage_caption) == 1
    assert headerimage_caption[0].text.strip().startswith('Freiheit')


def test_zar_article_toc_has_fallback_title(testbrowser):
    browser = testbrowser('/arbeit/article/paginated-nopagetitle/seite-2')

    toc_items = browser.cssselect('.article-toc__item')
    assert len(toc_items) == 4

    toc_item_1 = toc_items[0].cssselect('span')[0]
    assert toc_item_1.text.strip() == 'Mehrseitiger Artikel ohne Seiten-Titel'

    toc_item_2 = toc_items[1].cssselect('span')[0]
    assert toc_item_2.text.strip() == 'Seite 2'


def test_zar_article_with_dark_header_has_correct_structure(testbrowser):
    browser = testbrowser('/arbeit/article/header-dark')
    # we want to see one header, which has a modifier
    assert len(browser.cssselect('.article-header--dark')) == 1
    # the article heading items are inside the header-container
    assert len(browser.cssselect(
        '.article-header--dark > .article-heading')) == 1
    # image should be outside/behind the header (because the figure caption
    # has a bright background)
    assert len(browser.cssselect(
        '.article-header--dark + .article__media--header-image')) == 1


def test_zar_article_header_on_second_page_has_correct_structure(testbrowser):
    browser = testbrowser('/arbeit/article/header-dark/seite-2')
    assert len(browser.cssselect('.article-header--dark')) == 1
    assert len(browser.cssselect(
        '.article-header--dark .article__page-teaser')) == 1
    assert len(browser.cssselect('.article__media--header-image')) == 0


def test_zar_article_renders_nextread_correctly(testbrowser):
    browser = testbrowser('/arbeit/article/simple-nextread')
    assert len(browser.cssselect('.nextread')) == 1
    assert len(browser.cssselect('.nextread__lead')) == 1
    assert len(browser.cssselect('.nextread__media')) == 1
    assert len(browser.cssselect('.nextread .series-label')) == 1
    assert len(browser.cssselect('.nextread__kicker')) == 1
    assert len(browser.cssselect('.nextread__title')) == 1
    assert len(browser.cssselect('.nextread__byline')) == 1
    assert len(browser.cssselect('.nextread__text')) == 0


def test_zar_article_renders_nextread_without_fallback_image(testbrowser):
    browser = testbrowser('/arbeit/article/simple-nextread-noimage')
    assert len(browser.cssselect('.nextread__media')) == 0


def test_zar_article_nextread_provides_expected_webtrekk_string(
        selenium_driver, testserver):
    url = testserver.url + '{}#debug-clicktracking'
    driver = selenium_driver
    driver.set_window_size(1000, 800)
    driver.get(url.format(('/arbeit/article/simple-nextread')))

    try:
        WebDriverWait(driver, 3).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '.nextread')))
    except TimeoutException:
        assert False, 'nextread must be present'

    link = driver.find_element_by_css_selector('.nextread__combined-link')
    link.click()
    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data.startswith(
        'stationaer.articlebottom.editorial-nextread...text')


def test_zar_article_advertising_nextread_provides_expected_webtrekk_string(
        selenium_driver, testserver):
    url = testserver.url + '{}#debug-clicktracking'
    driver = selenium_driver
    driver.set_window_size(1000, 800)
    driver.get(url.format(('/arbeit/article/simple-verlagsnextread')))

    try:
        WebDriverWait(driver, 3).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '.nextread-advertisement__button')))
    except TimeoutException:
        assert False, 'nextread-advertisement must be present'

    link = driver.find_element_by_css_selector(
        '.nextread-advertisement__button')
    link.click()
    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data.startswith(
        'stationaer.articlebottom.publisher-nextread.button.1.jobs_finden')


def test_zar_article_podcast_header_renders_correctly(testbrowser):
    browser = testbrowser('/arbeit/article/podcast')
    assert len(browser.cssselect('.article-heading--podcast')) == 1
    assert len(browser.cssselect('.article-heading__container')) == 1
    assert len(browser.cssselect('.article-heading__headline--podcast')) == 1
    assert len(browser.cssselect('.article-heading__series--podcast')) == 1
    assert len(browser.cssselect('.article-heading__kicker--podcast')) == 1
    assert len(browser.cssselect('.article-heading__title--podcast')) == 1
    assert len(browser.cssselect('.article-heading__podcast-player')) == 1
    assert len(browser.cssselect('.article-heading__link-series')) == 1

    player = browser.cssselect('script.podigee-podcast-player')[0]
    assert player.get('data-configuration') == 'podigee_player_6853'
    assert '"theme": "zon-minimal"' in browser.contents
    browser = testbrowser('/arbeit/article/podcast-no-series')
    assert not browser.cssselect('.article-heading__link-series')


def test_podcast_header_should_omit_podlove_button_if_no_feeds(testbrowser):
    with mock.patch('zeit.web.core.podigee.Podigee.get_podcast') as podcast:
        podcast.return_value = {}
        browser = testbrowser('/arbeit/article/podcast')
    assert not browser.cssselect('script.podlove-subscribe-button')


def test_zar_article_should_provide_jobboxticker(
        testserver, monkeypatch, file_from_data):

    def myget(url, timeout=1):
        xml = lxml.etree.parse(file_from_data('/jobboxticker/feed.rss'))
        mymock = mock.Mock()
        mymock.content = lxml.etree.tostring(xml)
        return mymock

    monkeypatch.setattr(requests, 'get', myget)

    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/arbeit/article/jobbox-ticker')
    body = zeit.content.article.edit.interfaces.IEditableBody(article)
    jobbox_ticker = zeit.web.core.interfaces.IFrontendBlock(body[1])
    ticker_item = list(jobbox_ticker.items)[0]
    assert 'my_title' == ticker_item.title
    assert 'my_text' == ticker_item.text
    assert 'http://my_landing_page' == jobbox_ticker.landing_page_url


def test_zar_article_should_show_jobboxticker(testbrowser):
    browser = testbrowser('/arbeit/article/jobbox-ticker')
    assert browser.cssselect('.jobbox-ticker')
    assert browser.cssselect('.jobbox-ticker-item__title')


def test_zar_article_should_hide_empty_jobboxticker(testbrowser, monkeypatch):

    def myget(url, timeout=1):
        mymock = mock.Mock()
        mymock.content = ''
        return mymock

    monkeypatch.setattr(requests, 'get', myget)
    browser = testbrowser('/arbeit/article/jobbox-ticker')
    assert browser.cssselect('.jobbox-ticker__heading')
    assert not browser.cssselect('.jobbox-ticker-item__container')


def test_zar_column_article_has_correct_structure(testbrowser):
    browser = testbrowser('/arbeit/article/column')
    select = browser.cssselect
    assert len(select('.article-header-column')) == 1
    assert len(select('.article-header-column__box')) == 1
    assert len(select('.article-header-column__heading')) == 1
    assert len(select('.article-header-column__kicker')) == 1
    assert len(select('.article-header-column__title')) == 1

    assert len(select('.article-header__media--column')) == 1
    assert len(select(
        '.article-header-column figcaption.figcaption--hidden')) == 1

    assert len(select('.summary')) == 1
    assert len(select('.metadata')) == 1

    # We set our own byline on unusual position, and suppress the default one
    assert len(select('.article-header-column__byline')) == 1
    assert len(select('.byline')) == 0


def test_zar_column_article_has_correct_structure_on_page2(testbrowser):
    browser = testbrowser('/arbeit/article/column/seite-2')
    select = browser.cssselect
    assert len(select('.article-header-column')) == 1
    assert len(select('.article-header-column__box')) == 1
    assert len(select('.article-header-column__heading')) == 1
    assert len(select('.article-header-column__kicker')) == 1
    assert len(select('.article-header-column__title')) == 1

    assert len(select('.article-header__media--column')) == 1
    assert len(select(
        '.article-header-column figcaption.figcaption--hidden')) == 1

    assert len(select('.summary')) == 0
    assert len(select('.metadata')) == 0

    # We set our own byline on unusual position, and suppress the default one
    assert len(select('.article-header-column__byline')) == 1
    assert len(select('.byline')) == 0
