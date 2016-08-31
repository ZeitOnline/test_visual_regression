# -*- coding: utf-8 -*-
import pytest
import re
import zope.component

import zeit.solr.interfaces

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import InvalidSwitchToTargetException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


@pytest.mark.parametrize(
    'teaser', [
        # teaser-classic solo
        ('.teaser-classic .teaser-classic__combined-link',
         '1.1.1.solo-teaser-classic-zplus.text'),
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
         '4.1.1.parquet-teaser-large-zplus.text')
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
        ('.nav__tags a',
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


@pytest.mark.xfail(reason='Random loading issues in Selenium.')
def test_video_stage_provides_expected_webtrekk_string(
        selenium_driver, testserver):
    url = testserver.url + '{}#debug-clicktracking'
    driver = selenium_driver
    driver.set_window_size(980, 800)
    driver.get(url.format('/zeit-online/video-stage'))

    link = driver.find_element_by_class_name('video-large__combined-link')
    link.click()

    try:
        WebDriverWait(driver, 3).until(
            expected_conditions.frame_to_be_available_and_switch_to_it(
                (By.CLASS_NAME, 'video-player__iframe')))
    except (TimeoutException, InvalidSwitchToTargetException):
        assert False, 'iframe must be available'

    driver.switch_to.default_content()
    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data.startswith(
        'stationaer.video.large.alternative_nobelpreistraeger.brightcove..')
    assert tracking_data.endswith((
        '/video/2014-01/1953013471001/'
        'foto-momente-die-stille-schoenheit-der-polarlichter'))


@pytest.mark.xfail(reason='Random loading issues in Selenium.')
def test_video_block_provides_expected_webtrekk_string(
        selenium_driver, testserver):
    url = testserver.url + '{}#debug-clicktracking'
    driver = selenium_driver
    driver.set_window_size(980, 800)

    # test ZON article
    driver.get(url.format('/zeit-online/article/zeit'))

    try:
        WebDriverWait(driver, 3).until(
            expected_conditions.element_to_be_clickable(
                (By.CLASS_NAME, 'vjs-big-play-button')))
    except TimeoutException:
        assert False, 'Play button must be clickable'

    button = driver.find_element_by_class_name('vjs-big-play-button')
    button.click()

    try:
        WebDriverWait(driver, 3).until(
            expected_conditions.invisibility_of_element_located(
                (By.CLASS_NAME, 'vjs-big-play-button')))
    except TimeoutException:
        assert False, 'Play button must be hidden (video must be playing)'

    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data.startswith(
        'stationaer.video.large..brightcove..')
    assert tracking_data.endswith((
        '/video/2014-01/3035864892001/reporter-on-ice-zeit-online-'
        'sportreporter-christian-spiller-uebt-skispringen'))

    # test Campus article
    driver.get(url.format('/campus/article/video'))

    try:
        WebDriverWait(driver, 3).until(
            expected_conditions.element_to_be_clickable(
                (By.CLASS_NAME, 'vjs-big-play-button')))
    except TimeoutException:
        assert False, 'Play button must be clickable'

    button = driver.find_element_by_class_name('vjs-big-play-button')
    button.click()

    try:
        WebDriverWait(driver, 3).until(
            expected_conditions.invisibility_of_element_located(
                (By.CLASS_NAME, 'vjs-big-play-button')))
    except TimeoutException:
        assert False, 'Play button must be hidden (video must be playing)'

    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data.startswith(
        'stationaer.video.large..brightcove..')
    assert tracking_data.endswith((
        '/video/2014-01/3035864892001/reporter-on-ice-zeit-online-'
        'sportreporter-christian-spiller-uebt-skispringen'))


@pytest.mark.xfail(reason='Random loading issues in Selenium.')
def test_video_page_provides_expected_webtrekk_string(
        selenium_driver, testserver):
    url = testserver.url + '{}#debug-clicktracking'
    driver = selenium_driver
    driver.set_window_size(980, 800)
    driver.get(url.format(('/video/2014-01/1953013471001/motorraeder-foto-'
                           'momente-die-stille-schoenheit-der-polarlichter')))

    try:
        WebDriverWait(driver, 3).until(
            expected_conditions.frame_to_be_available_and_switch_to_it(
                (By.CLASS_NAME, 'video-player__iframe')))
    except (TimeoutException, InvalidSwitchToTargetException):
        assert False, 'iframe must be available'

    driver.switch_to.default_content()
    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data.startswith(
        'stationaer.video.large.alternative_nobelpreistraeger.brightcove..')
    assert tracking_data.endswith((
        '/video/2014-01/1953013471001/'
        'motorraeder-foto-momente-die-stille-schoenheit-der-polarlichter'))


@pytest.mark.parametrize(
    'teasers', [
        ('.teaser-fullwidth a',
         '1.1.1.solo-teaser-fullwidth-zplus.image'),
        ('.teaser-fullwidth-column a',
         '2.1.1.solo-teaser-fullwidth-column-zplus.image'),
        ('.teaser-topic .teaser-topic-main a',
         '5.1.1.topic-teaser-topic-main.text'),
        ('.teaser-topic .teaser-topic-item a',
         '5.1.2.topic-teaser-topic-item.text'),
        ('.teaser-topic .teaser-topic-item[data-zplus="true"] a',
         '5.1.3.topic-teaser-topic-item-zplus.text'),
        ('.teaser-gallery[data-zplus="true"] a',
         '6.1.2.gallery-teaser-gallery-zplus.image'),
        ('.parquet-teasers .teaser-large  a',
         '7.1.1.parquet-teaser-large-zplus.text')
    ])
def test_zplus_provides_expected_webtrekk_strings(
        selenium_driver, testserver, teasers):

    driver = selenium_driver
    driver.set_window_size(900, 800)
    driver.get('%s/zeit-online/centerpage/zplus'
               '#debug-clicktracking' % testserver.url)

    try:
        WebDriverWait(driver, 5).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, teasers[0])))
    except TimeoutException:
        assert False, 'Element not locateable in 5 sec.'
    else:
        teaser_el = driver.find_element_by_css_selector(teasers[0])
        teaser_el.click()
        track_str = driver.execute_script("return window.trackingData")
        assert('tablet.' + teasers[1] in track_str)


def test_cp_area_pagination_provides_expected_webtrekk_string(
        selenium_driver, testserver):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [
        ({'uniqueId':
         'http://xml.zeit.de/zeit-online/article/01'}) for i in range(60)]

    driver = selenium_driver
    driver.set_window_size(1024, 800)
    driver.get('%s/thema/berlin#debug-clicktracking' % testserver.url)

    links = driver.find_elements_by_css_selector('.pager--ranking a')
    labels = ['naechste_seite', '2', '3']

    for index, link in enumerate(links):
        link.click()
        tracking_data = driver.execute_script("return window.trackingData")
        assert('stationaer.area-pager....' + labels[index] in tracking_data)


def test_news_pagination_provides_expected_webtrekk_string(
        selenium_driver, testserver):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [
        ({'uniqueId':
         'http://xml.zeit.de/zeit-online/article/01'}) for i in range(2)]

    driver = selenium_driver
    driver.set_window_size(1024, 800)
    driver.get('%s/news/index#debug-clicktracking' % testserver.url)

    try:
        WebDriverWait(driver, 3).until(
            expected_conditions.element_to_be_clickable(
                (By.CSS_SELECTOR, '.pager--overview a')))
    except TimeoutException:
        assert False, 'pagination link must be clickable'

    link = driver.find_element_by_css_selector('.pager--overview a')
    link.click()
    tracking_data = driver.execute_script("return window.trackingData")
    assert('stationaer.area-pager....vorheriger_tag' in tracking_data)
