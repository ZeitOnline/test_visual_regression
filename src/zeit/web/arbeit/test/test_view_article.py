# -*- coding: utf-8 -*-
import pytest

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


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
    arrows = browser.cssselect('.quote__source-arrow')
    assert len(quotes) == 4
    assert len(arrows) == 2


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


def test_zar_article_paginated_has_headerimage_only_on_first_page(testbrowser):
    browser = testbrowser('/arbeit/article/01-digitale-nomaden/')
    assert len(browser.cssselect('.article__media--header-image')) == 1

    browser = testbrowser('/arbeit/article/01-digitale-nomaden/seite-2')
    assert not browser.cssselect('.article__media--header-image')

    browser = testbrowser(
        '/arbeit/article/01-digitale-nomaden/komplettansicht')
    assert len(browser.cssselect('.article__media--header-image')) == 1


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
