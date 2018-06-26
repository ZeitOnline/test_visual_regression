# This test needs to run against an actual staging environment,
# i.e. already running servers and real hostnames (not just "localhost").
# The test requires a registered and confirmed user (state=active).

import pytest
import requests
import time
import zope.testbrowser.browser

from datetime import datetime

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


def test_responsecode(config):
    resp = requests.get(
        '{}/index'.format(config['BASE_URL']), timeout=config['TIMEOUT'])
    assert resp.status_code == 200
    resp = requests.get(
        '{}/zeit-magazin/index'.format(config['BASE_URL']),
        timeout=config['TIMEOUT'])
    assert resp.status_code == 200
    resp = requests.get(
        '{}/campus/index'.format(config['BASE_URL']),
        timeout=config['TIMEOUT'])
    assert resp.status_code == 200


def test_newsfeeds(config):
    resp = requests.get(
        '{}/administratives/socialflow-zmo/rss-socialflow-facebook'.format(
            config['NEWSFEED_BASE_URL']))
    assert resp.status_code == 200

    resp = requests.get(
        '{}/administratives/socialflow-zmo/rss-socialflow-facebook-zmo'.format(
            config['NEWSFEED_BASE_URL']))
    assert resp.status_code == 200


def test_login_and_logout(config):
    b = zope.testbrowser.browser.Browser()
    b.mech_browser.set_handle_robots(False)
    b.open('{}/anmelden'.format(config['MEMBER_BASE_URL']))
    b.getControl(name='email').value = config['MEMBER_USERNAME']
    b.getControl(name='pass').value = config['MEMBER_PASSWORD']
    b.getControl('Anmelden').click()
    assert '{}/konto'.format(config['BASE_URL']) in b.url

    # logout
    b.open('{}/abmelden'.format(config['MEMBER_BASE_URL']))
    assert 'Logout erfolgreich' in b.contents


def test_infographic(config):
    b = zope.testbrowser.browser.Browser()
    b.open('{}/anmelden'.format(config['MEMBER_BASE_URL']))
    b.getControl(name='email').value = config['MEMBER_USERNAME']
    b.getControl(name='pass').value = config['MEMBER_PASSWORD']
    b.getControl('Anmelden').click()
    assert '{}/konto'.format(config['BASE_URL']) in b.url

    b.open(
        '{}/2016/40/globalisierung-arm-reich-entwicklung-'
        'soziale-ungleichheit'.format(config['BASE_URL']))
    assert '<div class="infographic">' in b.contents

    # logout
    b.open('{}/abmelden'.format(config['MEMBER_BASE_URL']))
    assert 'Logout erfolgreich' in b.contents


@pytest.mark.skipif(datetime.now() < datetime(2018, 5, 14),
                    reason="Community needs this repaired by Tobias Kabbeck")
def test_commenting(config):
    if config['ENV'] == 'PRODUCTION':
        assert True
    else:
        b = zope.testbrowser.browser.Browser()
        b.open('{}/anmelden'.format(config['MEMBER_BASE_URL']))
        b.getControl(name='email').value = config['MEMBER_USERNAME']
        b.getControl(name='pass').value = config['MEMBER_PASSWORD']
        b.getControl('Anmelden').click()
        assert '{}/konto'.format(config['BASE_URL']) in b.url

        b.open('{}/sport/fussball/2010-04/kaiserslautern-marcel-reif'.format(
            config['BASE_URL']))
        assert 'id="comment-form"' in b.contents

        testcomment = 'mein-testkommentar {}'.format(time.strftime("%c"))

        b.getForm(id='comment-form').getControl(
            name='comment').value = testcomment
        b.getForm(id='comment-form').getControl('Kommentar senden').click()
        assert '?cid=' in b.url
        assert testcomment in b.contents

        # logout
        b.open('{}/abmelden'.format(config['MEMBER_BASE_URL']))
        assert 'Logout erfolgreich' in b.contents


def test_videostage_thumbnail_should_be_replaced(config, selenium_driver):
    driver = selenium_driver
    driver.get('{}/video/index'.format(config['BASE_URL']))
    article = driver.find_element_by_css_selector(
        '#video-stage .video-large')
    videolink = driver.find_element_by_css_selector(
        '#video-stage .video-large figure')
    thumbnail = article.find_element_by_css_selector(
        '.video-thumbnail__media-item')
    videolink.click()
    try:
        WebDriverWait(driver, config['TIMEOUT']).until(
            expected_conditions.staleness_of(thumbnail))
        assert True
    except TimeoutException:
        assert False, 'Thumbnail not replaced by video'


def test_video_should_load_on_video_single_page(config, selenium_driver):
    driver = selenium_driver
    driver.get(
        '{}/video/2018-04/5773677245001/'
        'antisemitismus-hast-du-keine-angst'.format(
            config['BASE_URL']))
    video_visible_ec = expected_conditions.presence_of_element_located(
        (By.CLASS_NAME, 'vjs-control-bar'))

    try:
        WebDriverWait(driver, config['TIMEOUT']).until(video_visible_ec)
        assert True
    except TimeoutException:
        assert False, 'Video player not loaded'


def test_asset_cache_header(config):
    response = requests.get('{}/assets/latest/css/web.site/screen.css'.format(
        config['BASE_URL']))
    assert response.status_code == 200
    assert response.headers.get(
        'Cache-Control', '') == 'max-age=31536000, immutable'


def test_responsecode_404(config):
    resp = requests.get('{}/gipsnet'.format(config['BASE_URL']))
    assert resp.status_code == 404


def test_centerpages_contain_teasers(config, testbrowser):

    browser = testbrowser('{}/index'.format(config['BASE_URL']))
    assert len(browser.cssselect('article[class*=teaser]')) > 50

    browser = testbrowser('{}/politik/index'.format(config['BASE_URL']))
    assert len(browser.cssselect('article[class*=teaser]')) > 20

    browser = testbrowser(
        '{}/zeit-magazin/index'.format(config['BASE_URL']))
    assert len(browser.cssselect('article[class*=teaser]')) > 20

    browser = testbrowser('{}/campus/index'.format(config['BASE_URL']))
    assert len(browser.cssselect('article[class*=teaser]')) > 20


def test_topicpage_contains_teasers(config, testbrowser):
    browser = testbrowser('{}/thema/us-wahl'.format(config['BASE_URL']))
    assert len(browser.cssselect('article[class*=newsteaser]')) == 8
    if config['ENV'] == 'STAGING':
        assert len(browser.cssselect('article[class*=teaser-small]')) == 6
    else:
        assert len(browser.cssselect('article[class*=teaser-small]')) == 26


def test_search_results_page_contains_teasers(config, testbrowser):
    # we have no indexed content on staging
    if config['ENV'] == 'STAGING':
        assert True
    else:
        browser = testbrowser(
            '{}/suche/index?q=europa'.format(config['BASE_URL']))
        assert len(browser.cssselect('article[class*=teaser]'))

        browser = testbrowser(
            '{}/suche/index?q=&mode=7d&type=article&type=video'.format(
                config['BASE_URL']))
        assert len(browser.cssselect('article[class*=teaser]'))


def test_configured_redirects(config):
    current_year = datetime.now().year
    resp = requests.head('{}/archiv'.format(config['BASE_URL']),
                         allow_redirects=False)
    assert resp.headers['Location'] == 'https://www.zeit.de/{}/index'.format(
        current_year)
    resp = requests.head('{}/ZEITmagazin/'.format(config['BASE_URL']),
                         allow_redirects=False)
    assert resp.headers['Location'] == 'https://www.zeit.de/zeit-magazin/index'
    resp = requests.head('{}/archiv/2000/foo'.format(config['BASE_URL']),
                         allow_redirects=False)
    assert resp.headers['Location'] == 'https://www.zeit.de/2000/foo'


def test_iq_ehash_returns_expected_string(
        config, selenium_driver):
    driver = selenium_driver
    script = 'return window.Zeit.iq_ehash'
    # request some arbitrary article page and set loggedin-cookie
    driver.get('{}/news/index'.format(config['BASE_URL']))
    loginlink = driver.find_element_by_css_selector('.nav__login a')
    loginlink.click()
    # enter credentials
    email = driver.find_element_by_id('login_email')
    password = driver.find_element_by_id('login_pass')
    submitbtn = driver.find_element_by_css_selector('input.submit-button.log')
    email.send_keys(config['MEMBER_USERNAME'])
    password.send_keys(config['MEMBER_PASSWORD'])
    submitbtn.click()
    iq_ehash = driver.execute_script(script)
    # presence of hash depends on toggle 'iqd_touchpoint'
    if iq_ehash:
        if config['ENV'] == 'PRODUCTION':
            assert u'102-9fecd066a29d28ff481de0b82664d53a11c04aafc2400be00' \
                'ff77a8a2c6c3dbe' == iq_ehash
        else:
            assert u'102-2d0d19d7f9d0e5e5e889f3d68922bf54f57f494a2a75daea' \
                '18c03f5386cbf467' == iq_ehash


def test_zar_hp_should_render(config, selenium_driver):
    driver = selenium_driver
    driver.get(
        '{}/arbeit/index'.format(
            config['BASE_URL']))
    cp_visible = expected_conditions.presence_of_element_located(
        (By.CLASS_NAME, 'main--centerpage'))

    try:
        WebDriverWait(driver, config['TIMEOUT']).until(cp_visible)
        assert True
    except TimeoutException:
        assert False, 'ZAR HP not rendered'


def test_centerpages_with_autoareas_contain_teasers(config, testbrowser):

    browser = testbrowser('{}/podcasts'.format(config['BASE_URL']))
    assert len(browser.cssselect('article[class*=teaser]')), 'no Podcasts'

    browser = testbrowser('{}/investigativ'.format(config['BASE_URL']))
    assert len(browser.cssselect('article[class*=teaser]')), 'no Investigativ'

    browser = testbrowser('{}/serie/fischer-im-recht'.format(
        config['BASE_URL']))
    assert len(browser.cssselect('article[class*=teaser]')), 'no Serie'


def test_homepage_has_buzzboxes_with_content(config, testbrowser):
    browser = testbrowser('{}/index'.format(config['BASE_URL']))
    # stagin content not in sync w/ production
    # TODO: Remove asap
    if config['ENV'] == 'STAGING':
        assert True
    else:
        assert len(browser.cssselect('#buzz-mostread .teaser-buzz')) == 3
        assert len(browser.cssselect('#buzz-comments .teaser-buzz')) == 3
        assert len(browser.cssselect('#buzz-shared .teaser-buzz')) == 3
        assert len(browser.cssselect('.buzzboard .teaser-buzzboard')) == 12
