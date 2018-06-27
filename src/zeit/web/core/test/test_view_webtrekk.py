# -*- coding: utf-8 -*-
import mock
import pyramid.decorator
import pyramid.interfaces
import pytest
import time
import zope.component

import zeit.solr.interfaces

import zeit.web.core.template

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import InvalidSwitchToTargetException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


@pytest.mark.parametrize(
    'teaser', [
        # teaser-classic solo
        ('.teaser-classic .teaser-classic__media-item',
         'solo.1.1.teaser-classic-zplus.image'),
        ('.teaser-classic .teaser-classic__combined-link',
         'solo.1.1.teaser-classic-zplus.text'),
        ('.teaser-classic .teaser-classic__commentcount',
         'solo.1.1.teaser-classic.comments'),
        # teaser-square minor
        # ('.cp-area--minor .teaser-square__media-item',
        #  'minor.2.1.teaser-square.image'),
        ('.cp-area--minor .teaser-square__combined-link',
         'minor.2.1.teaser-square.text'),
        ('.cp-area--minor .teaser-square__button',
         'minor.2.1.teaser-square.button'),
        # teaser-small major
        ('.cp-area--major .teaser-small__media-item',
         'major.2.1.teaser-small.image'),
        ('.cp-area--major .teaser-small__combined-link',
         'major.2.1.teaser-small.text'),
        ('.cp-area--major .teaser-small__commentcount',
         'major.2.1.teaser-small.comments'),
        # teaser-small parquet
        ('.parquet-teasers .teaser-small .teaser-small__combined-link',
         'parquet-titel.3.1.teaser-small.text'),
        # teaser-large parquet
        ('.parquet-teasers .teaser-large .teaser-large__commentcount',
         'parquet-titel.4.2.teaser-large.comments'),
        ('.parquet-teasers .teaser-large .teaser-large__combined-link',
         'parquet-titel.4.1.teaser-large-zplus.text')
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

    # exclude testing for images on mobile
    if 'teaser-small__media-item' not in teaser[0]:
        teaser_el = driver.find_element_by_css_selector(teaser[0])
        teaser_el.click()
        track_str = driver.execute_script("return window.trackingData")
        assert('mobile.' + teaser[1] in track_str)

    # phablet
    driver.set_window_size(520, 800)

    teaser_el = driver.find_element_by_css_selector(teaser[0])
    driver.execute_script('arguments[0].click();', teaser_el)
    track_str = driver.execute_script("return window.trackingData")
    assert('phablet.' + teaser[1] in track_str)

    # tablet
    driver.set_window_size(800, 600)

    teaser_el = driver.find_element_by_css_selector(teaser[0])
    driver.execute_script('arguments[0].click();', teaser_el)
    track_str = driver.execute_script("return window.trackingData")
    assert('tablet.' + teaser[1] in track_str)

    # desktop
    driver.set_window_size(1000, 800)

    teaser_el = driver.find_element_by_css_selector(teaser[0])
    driver.execute_script('arguments[0].click();', teaser_el)
    track_str = driver.execute_script("return window.trackingData")
    assert('stationaer.' + teaser[1] in track_str)


@pytest.mark.parametrize(
    'teasers', [
        ('.teaser-classic .teaser-classic__combined-link',
         '/zeit-online/article/02'),
        ('.teaser-small .teaser-small__combined-link',
         '/zeit-online/article/01'),
        ('.teaser-square .teaser-square__combined-link',
         '/zeit-online/gallery/biga_1')
    ])
def test_cp_element_provides_expected_url_for_webtrekk(
        selenium_driver, testserver, teasers):

    driver = selenium_driver
    driver.set_window_size(400, 800)
    driver.get('%s/zeit-online/webtrekk-test-setup'
               '#debug-clicktracking' % testserver.url)
    hostname = testserver.url.replace('http://', '')

    try:
        WebDriverWait(driver, 5).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, teasers[0])))
    except TimeoutException:
        assert False, 'Element not locateable in 5 sec.'
    else:
        teaser_el = driver.find_element_by_css_selector(teasers[0])
        teaser_el.click()
        track_str = driver.execute_script('return window.trackingData;')
        assert track_str.endswith('|%s%s' % (hostname, teasers[1]))


def test_parquet_meta_provides_expected_webtrekk_strings(
        selenium_driver, testserver):

    driver = selenium_driver
    driver.get('%s/zeit-online/webtrekk-test-setup'
               '#debug-clicktracking' % testserver.url)
    driver.set_window_size(1000, 800)

    title = driver.find_element_by_css_selector('.parquet-meta__title')
    title.click()
    track_str = driver.execute_script("return window.trackingData")
    assert ('stationaer.parquet-titel.3.0.1.title|%s/zeit-online/parquet'
            % testserver.url.replace('http://', '')) == track_str

    links = driver.find_elements_by_css_selector('.parquet-meta__links a')

    for x in range(3):
        links[x].click()
        track_str = driver.execute_script("return window.trackingData")
        identifier = 'stationaer.parquet-titel.3.0.{}.topiclink|{}'.format(
            x + 2, links[x].get_attribute('href').replace('https://', ''))
        assert identifier == track_str

    title = driver.find_element_by_css_selector('.parquet-meta__more-link')
    title.click()
    track_str = driver.execute_script("return window.trackingData")
    assert track_str == (
        'stationaer.parquet-titel.3.0.5.morelink|www.zeit.de/politik/index')


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
    assert track_str == 'mobile.minor.2..buzz-box.aufsteigend|#buzz-box'

    link = driver.find_element_by_css_selector('.teaser-buzz__combined-link')
    link.click()
    track_str = driver.execute_script("return window.trackingData")
    assert track_str.startswith('mobile.minor.2.4.teaser-buzz.text|')
    assert track_str.endswith('/zeit-online/cp-content/liveblog-live')

    # desktop
    driver.set_window_size(1000, 800)
    link.click()
    track_str = driver.execute_script("return window.trackingData")
    assert track_str.startswith('stationaer.minor.2.4.teaser-buzz.text|')
    assert track_str.endswith('/zeit-online/cp-content/liveblog-live')


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
    driver.set_window_size(1000, 800)

    nav_el = driver.find_element_by_css_selector(navi[0])
    nav_el.click()
    track_str = driver.execute_script("return window.trackingData")
    assert('stationaer.' + navi[1] in track_str)


@pytest.mark.parametrize(
    'article', [
        # serie
        ('.article-series__heading',
         'articleheader.series...chefsache'),
        # author
        ('.byline a',
         'articleheader.author.1_of_1..anne_mustermann'),
        # source
        ('.metadata__source a',
         'articleheader.source...erschienen_bei_vice|www.example.com/foo'),
        # comment link
        ('.metadata__commentcount',
         'articleheader.comments...42_kommentare|#comments'),
        # toc
        ('.article-toc__link',
         'article-toc.page_1_of_2...2'),
        # intext
        ('.paragraph a',
         'article.2.seite-1.paragraph.kuendigung|www.zeit.de/karriere'),
        # authorbox
        ('.authorbox a',
         'article.6.seite-1.authorbox.zur_autorenseite'),
        # infobox
        ('.infobox a',
         'article.9.seite-1.infobox.crystal_meth|#crystal-meth-1-tab'),
        # portraitbox
        ('.portraitbox a',
         'article.13.seite-1.portraitbox.pia_volk|piavolk.net'),
        # pagination
        ('.article-pagination__link',
         'article-pager.page_1_of_2...naechste_seite'),
        ('.article-pager a',
         'article-pager.page_1_of_2...2'),
        ('.article-pager__all a',
         'article-pager.page_1_of_2...all'),
        # tags
        ('.article-tags a',
         'articlebottom.article-tag.1..arbeitgeber'),
        # nextread
        ('.nextread a',
         'articlebottom.editorial-nextread...area-zplus'),
    ])
def test_article_elements_provide_expected_id_for_webtrekk(
        selenium_driver, testserver, article):

    driver = selenium_driver
    driver.get('%s/zeit-online/article/webtrekk-test#debug-clicktracking'
               % testserver.url)

    # prevent testfail at first run
    presence_art = expected_conditions.presence_of_element_located(
        (By.CLASS_NAME, 'article-series'))

    try:
        WebDriverWait(driver, 3).until(presence_art)
    except TimeoutException:
        assert False, 'Article must be visible'

    # don't test mobile and phablet here as some elements
    # aren't visible and we test the principle anyway

    # tablet
    driver.set_window_size(768, 800)

    article_el = driver.find_element_by_css_selector(article[0])
    driver.execute_script('arguments[0].click();', article_el)
    track_str = driver.execute_script("return window.trackingData")
    assert('tablet.' + article[1] in track_str)

    # desktop
    driver.set_window_size(1000, 800)

    article_el = driver.find_element_by_css_selector(article[0])
    driver.execute_script('arguments[0].click();', article_el)
    track_str = driver.execute_script("return window.trackingData")
    assert('stationaer.' + article[1] in track_str)


@pytest.mark.xfail(reason='Random loading issues in Selenium.')
def test_video_stage_provides_expected_webtrekk_string(
        selenium_driver, testserver):
    url = testserver.url + '{}#debug-clicktracking'
    driver = selenium_driver
    driver.set_window_size(1000, 800)
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
    driver.set_window_size(1000, 800)

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
    driver.set_window_size(1000, 800)
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
         'solo.1.1.teaser-fullwidth-zplus.image'),
        ('.teaser-fullwidth-column a',
         'solo.2.1.teaser-fullwidth-column-zplus.image'),
        ('.teaser-topic .teaser-topic-main a',
         'topic.5.1.teaser-topic-main.text'),
        ('.teaser-topic .teaser-topic-item a',
         'topic.5.2.teaser-topic-item.text'),
        ('.teaser-topic .teaser-topic-item[data-zplus] a',
         'topic.5.3.teaser-topic-item-zplus.text'),
        ('.teaser-gallery[data-zplus] a',
         'gallery.6.2.teaser-gallery-zplus.image'),
        ('.parquet-teasers .teaser-large  a',
         'parquet-z_parkett.7.1.teaser-large-zplus.text')
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
        teaser_el.send_keys(Keys.RETURN)
        track_str = driver.execute_script("return window.trackingData")
        assert('tablet.' + teasers[1] in track_str)


@pytest.mark.parametrize(
    'teasers', [
        ('.teaser-fullwidth a',
         'solo.1.1.teaser-fullwidth-zplus-register.image'),
        ('.teaser-fullwidth-column a',
         'solo.2.1.teaser-fullwidth-column-zplus-register.image'),
        ('.teaser-topic .teaser-topic-item[data-zplus] a',
         'topic.5.2.teaser-topic-item-zplus-register.text'),
        ('.parquet-teasers .teaser-large a',
         'parquet-z_parkett.7.1.teaser-large-zplus-register.text')
    ])
def test_zplus_registration_provides_expected_webtrekk_strings(
        selenium_driver, testserver, teasers):

    driver = selenium_driver
    driver.set_window_size(900, 800)
    driver.get('%s/zeit-online/centerpage/register'
               '#debug-clicktracking' % testserver.url)

    try:
        WebDriverWait(driver, 5).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, teasers[0])))
    except TimeoutException:
        assert False, 'Element not locateable in 5 sec.'
    else:
        teaser_el = driver.find_element_by_css_selector(teasers[0])
        driver.execute_script('arguments[0].click();', teaser_el)
        track_str = driver.execute_script("return window.trackingData;")
        assert('tablet.' + teasers[1] in track_str)


def test_cp_area_pagination_provides_expected_webtrekk_string(
        selenium_driver, testserver):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [
        ({'uniqueId':
          'http://xml.zeit.de/zeit-online/article/01'}) for i in range(60)]

    driver = selenium_driver
    driver.set_window_size(1024, 768)
    driver.get('%s/thema/berlin#debug-clicktracking' % testserver.url)

    try:
        WebDriverWait(driver, 5).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '.pager--ranking a')))
    except TimeoutException:
        assert False, 'pagination link must be present'

    links = driver.find_elements_by_css_selector('.pager--ranking a')
    labels = ['naechste_seite', '2', '3']

    assert len(links) == len(labels)

    for index, link in enumerate(links):
        link.click()
        tracking_data = driver.execute_script("return window.trackingData")
        assert tracking_data.startswith(
            'stationaer.area-pager.page_1_of_3...' + labels[index])


def test_news_pagination_provides_expected_webtrekk_string(
        selenium_driver, testserver):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [
        ({'uniqueId':
          'http://xml.zeit.de/zeit-online/article/01'}) for i in range(2)]

    driver = selenium_driver
    driver.set_window_size(1024, 768)
    driver.get('%s/news/index#debug-clicktracking' % testserver.url)

    try:
        WebDriverWait(driver, 3).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '.pager--overview a')))
    except TimeoutException:
        assert False, 'pagination link must be present'

    link = driver.find_element_by_css_selector('.pager--overview a')
    link.click()
    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data.startswith(
        'stationaer.area-pager.page_1_of_30...vorheriger_tag')


def test_article_pagination_provides_expected_webtrekk_string(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.set_window_size(1024, 768)
    driver.get('%s/zeit-online/article/paginated#debug-clicktracking'
               % testserver.url)

    try:
        WebDriverWait(driver, 3).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '.article-pagination a')))
    except TimeoutException:
        assert False, 'pagination link must be present'

    links = driver.find_elements_by_css_selector('.article-pagination a')
    labels = ['naechste_seite', '2', '3', 'all']

    assert len(links) == len(labels)

    for index, link in enumerate(links):
        link.click()
        tracking_data = driver.execute_script("return window.trackingData")
        assert tracking_data.startswith(
            'stationaer.article-pager.page_1_of_3...' + labels[index])


def test_article_table_of_contents_provides_expected_webtrekk_string(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.set_window_size(1024, 768)
    driver.get('%s/zeit-online/article/paginated#debug-clicktracking'
               % testserver.url)

    try:
        WebDriverWait(driver, 3).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '.article-toc a')))
    except TimeoutException:
        assert False, 'table of contents link must be present'

    links = driver.find_elements_by_css_selector('.article-toc a')
    labels = ['2', '3', 'all']

    assert len(links) == len(labels)

    for index, link in enumerate(links):
        link.click()
        tracking_data = driver.execute_script("return window.trackingData")
        assert tracking_data.startswith(
            'stationaer.article-toc.page_1_of_3...' + labels[index])


def test_comment_pagination_provides_expected_webtrekk_string(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.set_window_size(1024, 768)
    driver.get('%s/zeit-online/article/01#debug-clicktracking'
               % testserver.url)

    try:
        WebDriverWait(driver, 3).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '.comment-section .pager a')))
    except TimeoutException:
        assert False, 'comment pagination link must be present'

    links = driver.find_elements_by_css_selector('.comment-section .pager a')
    labels = ['weitere_kommentare', '2', '3', '4', '5', '8']

    assert len(links) == len(labels)

    for index, link in enumerate(links):
        link.click()
        tracking_data = driver.execute_script("return window.trackingData")
        assert tracking_data.startswith(
            'stationaer.comment_pager.page_1_of_8...' + labels[index])


def test_zmo_article_pagination_provides_expected_webtrekk_string(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.set_window_size(1024, 768)
    driver.get('%s/zeit-magazin/article/03/seite-3#debug-clicktracking'
               % testserver.url)

    try:
        WebDriverWait(driver, 3).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '.main-footer')))
    except TimeoutException:
        assert False, 'we will wait for the footer forever ...'

    links = driver.find_elements_by_css_selector('.article-pagination a')
    labels = ['naechste_seite', '1', '2', '4', '5', '6', '7', 'all']

    assert len(links) == len(labels)

    for index, link in enumerate(links):
        link.send_keys(Keys.RETURN)
        tracking_data = driver.execute_script("return window.trackingData")
        assert tracking_data.startswith(
            'stationaer.article-pager.page_3_of_7...' + labels[index])

    link = driver.find_element_by_css_selector('.comment-balloon__link')
    link.click()
    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data.startswith(
        'stationaer.comment-balloon.comments...0_kommentare')


def test_volume_overview_teaser_provides_expected_webtrekk_string(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.set_window_size(800, 600)
    driver.get('%s/2016/index#debug-clicktracking'
               % testserver.url)

    try:
        WebDriverWait(driver, 3).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '.volume-overview')))
    except TimeoutException:
        assert False, 'volume-overview must be present'

    links = driver.find_elements_by_css_selector(
        '.teaser-volume-overview')
    assert len(links) == 7

    links[0].click()
    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data.startswith(
        'tablet.volume-overview.2.1.teaser-volume-overview.49_2014|')
    assert tracking_data.endswith('/2014/49/index')

    links[1].click()
    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data.startswith(
        'tablet.volume-overview.2.2.teaser-volume-overview.52_2015|')
    assert tracking_data.endswith('/2015/52/index')

    links[2].click()
    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data.startswith(
        'tablet.volume-overview.2.3.teaser-volume-overview.01_2016|')
    assert tracking_data.endswith('/2016/01/index')


def test_volume_teaser_in_article_provides_expected_webtrekk_string(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.set_window_size(800, 600)
    driver.get('%s/zeit-online/article/zplus-zeit#debug-clicktracking'
               % testserver.url)

    try:
        WebDriverWait(driver, 3).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '.zplus-badge__link')))
    except TimeoutException:
        assert False, 'link must be present'

    link = driver.find_element_by_css_selector('.zplus-badge__link')
    link.click()
    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data.startswith(
        'tablet.articleheader.zplus-badge...exklusiv_fuer_abonnenten|')


def test_coverless_volume_teaser_in_article_provides_expected_webtrekk_string(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.set_window_size(800, 600)
    driver.get('%s/zeit-online/article/zplus-zon#debug-clicktracking'
               % testserver.url)

    # Wait explicity for --coverless, to enforce lading the new article.
    # Without it, the previous test page is still opened while testing.
    try:
        WebDriverWait(driver, 3).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '.zplus-badge__link')))
    except TimeoutException:
        assert False, 'link must be present'

    link = driver.find_element_by_css_selector('.zplus-badge__link')
    link.click()
    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data.startswith(
        'tablet.articleheader.zplus-badge_coverless'
        '...exklusiv_fuer_abonnenten|')


def test_volume_header_provides_expected_webtrekk_string(
        selenium_driver, testserver, monkeypatch):

    driver = selenium_driver
    driver.set_window_size(1200, 800)
    driver.get('%s/2016/01/index#debug-clicktracking' % testserver.url)

    try:
        WebDriverWait(driver, 3).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '.teaser-volumeteaser__link')))
    except TimeoutException:
        assert False, 'navigation link must be present'

    link = driver.find_element_by_css_selector('.teaser-volumeteaser__link')
    link.click()
    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data.startswith(
        'stationaer.volume-navigation.current-volume...'
        'lesen_sie_diese_ausgabe_als_e_paper_app_und_auf_dem_e_reader|'
        'premium.zeit.de/abo/diezeit/2016/01')

    link = driver.find_element_by_css_selector('.volume-heading-teaser a')
    link.click()
    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data.startswith(
        'stationaer.volume-header.teaser.1..sommer_in_berlin')


@pytest.mark.xfail(reason='Random loading issues in Selenium.')
def test_comment_form_provides_expected_webtrekk_string(
        selenium_driver, testserver, application):
    extensions = application.zeit_app.config.registry.getUtility(
        pyramid.interfaces.IRequestExtensions)
    with mock.patch.dict(extensions.descriptors, {
            'user': pyramid.decorator.reify(lambda x: {
                'name': 'john.doe',
                'mail': 'test@example.org',
                'ssoid': 123,
                'has_community_data': True,
                'uid': 123,
            })}):
        driver = selenium_driver
        driver.set_window_size(1024, 768)
        driver.get('%s/zeit-online/article/01#debug-clicktracking'
                   % testserver.url)

        try:
            WebDriverWait(driver, 3).until(
                expected_conditions.presence_of_element_located(
                    (By.ID, 'comment-form')))
        except TimeoutException:
            assert False, 'comment form must be present'

        form = driver.find_element_by_id('comment-form')

        # fill out comment
        form.find_element_by_tag_name('textarea').send_keys('Test')
        # submit form
        form.find_element_by_xpath('//input[@type="submit"]').click()

        tracking_data = driver.execute_script("return window.trackingData")
        assert tracking_data == (
            'stationaer.comment_form.2.1..kommentar_senden|#comments')


def test_inline_gallery_provides_expected_webtrekk_string(
        selenium_driver, testserver):
    pathname = '/zeit-online/article/inline-gallery'
    driver = selenium_driver
    driver.set_window_size(1024, 768)
    driver.get('{}{}#debug-clicktracking'.format(testserver.url, pathname))

    try:
        WebDriverWait(driver, 3).until(
            expected_conditions.presence_of_element_located(
                (By.CLASS_NAME, 'bx-wrapper')))
    except TimeoutException:
        assert False, 'inline gallery must be present'

    driver.find_element_by_class_name('bx-prev').click()
    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data.startswith(
        'stationaer.article.6.seite-1.inline-gallery.ein_bild_zurueck')
    assert tracking_data.endswith(pathname)

    driver.find_element_by_class_name('bx-next').click()
    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data.startswith(
        'stationaer.article.6.seite-1.inline-gallery.ein_bild_vor')
    assert tracking_data.endswith(pathname)

    driver.find_element_by_class_name('bx-overlay-prev').click()
    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data.startswith(
        'stationaer.article.6.seite-1.inline-gallery.ein_bild_zurueck')
    assert tracking_data.endswith(pathname)

    driver.find_element_by_class_name('bx-overlay-next').click()
    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data.startswith(
        'stationaer.article.6.seite-1.inline-gallery.ein_bild_vor')
    assert tracking_data.endswith(pathname)


def test_gallery_provides_expected_webtrekk_string(
        selenium_driver, testserver):
    pathname = '/zeit-online/gallery/biga_1'
    driver = selenium_driver
    driver.set_window_size(1024, 768)
    driver.get('{}{}#debug-clicktracking'.format(testserver.url, pathname))

    # prevent testfail on consecutive run
    try:
        WebDriverWait(driver, 5).until(
            expected_conditions.title_contains(
                'Das hab ich auf dem Schirm'))
    except TimeoutException:
        assert False, 'page must be loaded'

    try:
        WebDriverWait(driver, 3).until(
            expected_conditions.presence_of_element_located(
                (By.CLASS_NAME, 'bx-wrapper')))
    except TimeoutException:
        assert False, 'gallery must be present'

    driver.find_element_by_class_name('bx-next').click()
    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data.startswith(
        'stationaer.gallery.1.2.2.ein_bild_vor')
    assert tracking_data.endswith(pathname)

    # wait for sliding animation
    time.sleep(0.6)

    driver.find_element_by_class_name('bx-prev').click()
    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data.startswith(
        'stationaer.gallery.1.1.1.ein_bild_zurueck')
    assert tracking_data.endswith(pathname)

    # wait for sliding animation
    time.sleep(0.6)

    driver.find_element_by_class_name('bx-overlay-next').click()
    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data.startswith(
        'stationaer.gallery.2.2.2.ein_bild_vor')
    assert tracking_data.endswith(pathname)

    # wait for sliding animation
    time.sleep(0.6)

    driver.find_element_by_class_name('bx-overlay-prev').click()
    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data.startswith(
        'stationaer.gallery.2.1.1.ein_bild_zurueck')
    assert tracking_data.endswith(pathname)


def test_buzz_box_provides_expected_webtrekk_string(
        selenium_driver, testserver):
    pathname = '/zeit-online/buzz-box'
    driver = selenium_driver
    driver.set_window_size(1024, 768)
    driver.get('{}{}#debug-clicktracking'.format(testserver.url, pathname))

    try:
        WebDriverWait(driver, 3).until(
            expected_conditions.presence_of_element_located(
                (By.CLASS_NAME, 'buzz-accordion')))
    except TimeoutException:
        assert False, 'buzz boxes must be present'

    driver.find_elements_by_class_name('buzz-box__heading')[2].click()
    tracking_data = driver.execute_script("return window.trackingData")
    assert tracking_data == 'stationaer.minor.1..buzz' \
        '-box.meistkommentiert|#buzz-box'


def test_check_product_id_campaign_paywall_webtrekk(testbrowser):
    browser = testbrowser('/zeit-online/article/01?C1-Meter-Status=paywall')

    wt_zmc = browser.cssselect('form input[name="wt_zmc"]')[0]
    wt_val = wt_zmc.get('value')
    wt_ck = 'fix.int.zonaudev.diezeit.wall_abo.premium.bar_metered.link.zede'
    assert wt_val == wt_ck

    utm_content = browser.cssselect('form input[name="utm_content"]')[0]
    utm_val = utm_content.get('value')
    utm_ck = 'premium_bar_metered_link_zede'
    assert utm_val == utm_ck
