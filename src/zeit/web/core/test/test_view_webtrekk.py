# -*- coding: utf-8 -*-
import pyramid.testing
import pytest
import re

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


@pytest.mark.parametrize(
    'teaser', [
        # teaser-classic solo
        ('.teaser-classic .teaser-classic__combined-link',
         '1.1.1.solo-teaser-classic.text'),
        # teaser-square minor
        ('.teaser-square .teaser-square__combined-link',
         '2.2.1.minor-teaser-square.text'),
        # teaser-small major
        ('.teaser-small .teaser-small__combined-link',
         '2.1.1.major-teaser-small.text'),
        # teaser-small parquet
        ('.parquet-teasers .teaser-small .teaser-small__combined-link',
         '3.1.1.parquet-teaser-small.text'),
        # teaser-large parquet
        ('.parquet-teasers .teaser-large .teaser-large__combined-link',
         '4.1.1.parquet-teaser-large.text')
    ])
def test_cp_elements_provide_expected_id_for_webtrekk(
        selenium_driver, testserver, teaser):

    driver = selenium_driver
    driver.get('%s/zeit-online/webtrekk-test-setup#debug-clicktracking'
               % testserver.url)

    # prevent testfail at first run
    presence_cp = expected_conditions.presence_of_element_located(
        (By.CLASS_NAME, 'main--centerpage'))

    try:
        WebDriverWait(driver, 3).until(presence_cp)
    except TimeoutException:
        assert False, 'CP must be visible'

    # mobile
    driver.set_window_size(400, 800)

    teaser_el = driver.find_element_by_css_selector(teaser[0])
    teaser_el.click()
    track_str = driver.execute_script("return window.trackingData")
    assert('mobile.' + teaser[1] in track_str)

    # phablet
    driver.set_window_size(520, 800)

    teaser_el = driver.find_element_by_css_selector(teaser[0])
    teaser_el.click()
    track_str = driver.execute_script("return window.trackingData")
    assert('phablet.' + teaser[1] in track_str)

    # tablet
    driver.set_window_size(768, 800)

    teaser_el = driver.find_element_by_css_selector(teaser[0])
    teaser_el.click()
    track_str = driver.execute_script("return window.trackingData")
    assert('tablet.' + teaser[1] in track_str)

    # desktop
    driver.set_window_size(980, 800)

    teaser_el = driver.find_element_by_css_selector(teaser[0])
    teaser_el.click()
    track_str = driver.execute_script("return window.trackingData")
    assert('stationaer.' + teaser[1] in track_str)


def test_cp_element_provides_expected_url_for_webtrekk(
        selenium_driver, testserver):

    driver = selenium_driver
    driver.get('%s/zeit-online/webtrekk-test-setup'
               '#debug-clicktracking' % testserver.url)
    driver.set_window_size(980, 800)

    teaser_el = driver.find_element_by_css_selector('.teaser-classic a')
    teaser_el.click()
    track_str = driver.execute_script("return window.trackingData")
    assert('/zeit-online/article/02' in track_str)


def test_parquet_meta_provides_expected_webtrekk_strings(
        selenium_driver, testserver):

    driver = selenium_driver
    driver.get('%s/zeit-online/webtrekk-test-setup'
               '#debug-clicktracking' % testserver.url)
    driver.set_window_size(980, 800)

    title = driver.find_element_by_css_selector('.parquet-meta__title')
    title.click()
    track_str = driver.execute_script("return window.trackingData")
    assert(re.search('stationaer.parquet.1.1..titel|'
           '.*/zeit-online/parquet', track_str))

    link = driver.find_element_by_css_selector('.parquet-meta__links a')
    link.click()
    track_str = driver.execute_script("return window.trackingData")
    assert('stationaer.parquet.2.1..topiclink'
           '|www.zeit.de/themen/krise-griechenland' in track_str)


def test_buzzboard_provides_expected_webtrekk_strings(
        selenium_driver, testserver):

    driver = selenium_driver
    driver.get('%s/zeit-online/webtrekk-test-setup'
               '#debug-clicktracking' % testserver.url)

    # mobile
    driver.set_window_size(400, 800)

    header = driver.find_element_by_css_selector('.buzz-box__heading')
    header.click()
    track_str = driver.execute_script("return window.trackingData")
    assert(re.search('mobile.....buzz-box__heading.aufsteigend|'
           '.*/zeit-online/buzz-box#buzz-trend', track_str))

    link = driver.find_element_by_css_selector('.teaser-buzz__combined-link')
    link.click()
    track_str = driver.execute_script("return window.trackingData")
    assert(re.search('mobile.1.2.2.minor-teaser-buzz.text|'
           '.*/zeit-online/article/01', track_str))

    # desktop
    driver.set_window_size(980, 800)
    link.click()
    track_str = driver.execute_script("return window.trackingData")
    assert(re.search('stationaer.1.2.2.minor-teaser-buzz.text|'
           '.*/zeit-online/article/01', track_str))


@pytest.mark.parametrize(
    'navi', [
        # classifieds
        ('.nav__classifieds a',
         'topnav.classifieds.1..abo'),
        # services
        ('.nav__services a',
         'topnav.services.1..e_paper'),
        # logo
        ('.header__brand a',
         'topnav.lead.1..logo'),
        # primary-nav
        ('.nav__ressorts a',
         'topnav.mainnav.1..politik'),
        # tags
        ('*[data-ct-row="article-tag"] a',
         'topnav.article-tag.1..griechenland_krise')
    ])
def test_navi_provides_expected_webtrekk_strings(
        selenium_driver, testserver, navi):

    driver = selenium_driver
    driver.get('%s/zeit-online/webtrekk-test-setup'
               '#debug-clicktracking' % testserver.url)
    driver.set_window_size(980, 800)

    nav_el = driver.find_element_by_css_selector(navi[0])
    nav_el.click()
    track_str = driver.execute_script("return window.trackingData")
    assert('stationaer.' + navi[1] in track_str)


@pytest.mark.parametrize(
    'article', [
        # intext
        ('.paragraph a',
         'intext.2/seite-1...cyborgs|www.zeit.de/digital'),
        # toc
        ('.article-toc__link',
         'article-toc....2'),
        # nextread
        ('.nextread a',
         'articlebottom.editorial-nextread...area'),
    ])
def test_article_elements_provide_expected_id_for_webtrekk(
        selenium_driver, testserver, article):

    driver = selenium_driver
    driver.get('%s/campus/article/paginated#debug-clicktracking'
               % testserver.url)

    # prevent testfail at first run
    presence_art = expected_conditions.presence_of_element_located(
        (By.CLASS_NAME, 'main--article'))

    try:
        WebDriverWait(driver, 3).until(presence_art)
    except TimeoutException:
        assert False, 'Article must be visible'

    # don't test mobile and phablet here as some elements
    # aren't visible and we test the principle anyway

    # tablet
    driver.set_window_size(768, 800)

    article_el = driver.find_element_by_css_selector(article[0])
    article_el.click()
    track_str = driver.execute_script("return window.trackingData")
    assert('tablet.' + article[1] in track_str)

    # desktop
    driver.set_window_size(980, 800)

    article_el = driver.find_element_by_css_selector(article[0])
    article_el.click()
    track_str = driver.execute_script("return window.trackingData")
    assert('stationaer.' + article[1] in track_str)