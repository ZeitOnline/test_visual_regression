# This test needs to run against an actual staging environment,
# i.e. already running servers and real hostnames (not just "localhost").
# The test requires a registered and confirmed user (state=active).

import requests
import time
import zope.testbrowser.browser

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

testuser = 'thomas.strothjohann+unmoderiert1@apps.zeit.de'
testpassword = 'unmoderierteins'


def test_endtoend_pass():
    pass


def test_endtoend_responsecode():
    resp = requests.get('http://www.staging.zeit.de/index')
    assert resp.status_code == 200
    resp = requests.get('http://www.staging.zeit.de/zeit-magazin/index')
    assert resp.status_code == 200
    resp = requests.get('http://www.staging.zeit.de/campus/index')
    assert resp.status_code == 200


def test_endtoend_newsfeeds():
    resp = requests.get(
        'http://newsfeed.staging.zeit.de/administratives/'
        'socialflow-zmo/rss-socialflow-facebook')
    assert resp.status_code == 200

    resp = requests.get(
        'http://newsfeed.staging.zeit.de/administratives/'
        'socialflow-zmo/rss-socialflow-facebook-zmo')
    assert resp.status_code == 200


def test_endtoend_centerpages_contain_teasers():
    browser = zope.testbrowser.browser.Browser()

    # OPTIMIZE: use real HTML/CSS selectors
    # assert len(browser.cssselect('article[class*=teaser]')) > 50

    browser.open('http://www.staging.zeit.de/index')
    assert browser.contents.count('<article class="teaser-') > 50

    browser.open('http://www.staging.zeit.de/politik/index')
    assert browser.contents.count('<article class="teaser-') > 20

    browser.open('http://www.staging.zeit.de/zeit-magazin/index')
    assert browser.contents.count('<article class="teaser-') > 20

    browser.open('http://www.staging.zeit.de/campus/index')
    assert browser.contents.count('<article class="teaser-') > 20


def test_endtoend_login_and_logout():
    b = zope.testbrowser.browser.Browser()
    b.open('https://meine.staging.zeit.de/anmelden')
    b.getControl(
        name='email').value = testuser
    b.getControl(name='password').value = testpassword
    b.getControl('Anmelden').click()
    assert 'http://www.staging.zeit.de/konto' in b.url
    # logout
    b.open('https://meine.staging.zeit.de/abmelden')
    assert 'Logout erfolgreich' in b.contents


def test_endtoend_infographic():
    b = zope.testbrowser.browser.Browser()
    b.open('https://meine.staging.zeit.de/anmelden')
    b.getControl(name='email').value = testuser
    b.getControl(name='password').value = testpassword
    b.getControl('Anmelden').click()
    assert 'http://www.staging.zeit.de/konto' in b.url

    b.open(
        'http://www.staging.zeit.de/2016/40/'
        'globalisierung-arm-reich-entwicklung-soziale-ungleichheit')
    assert '<div class="infographic">' in b.contents

    # logout
    b.open('https://meine.staging.zeit.de/abmelden')
    assert 'Logout erfolgreich' in b.contents


def test_endtoend_commenting():
    b = zope.testbrowser.browser.Browser()
    b.open('https://meine.staging.zeit.de/anmelden')
    b.getControl(name='email').value = testuser
    b.getControl(name='password').value = testpassword
    b.getControl('Anmelden').click()
    assert 'http://www.staging.zeit.de/konto' in b.url

    b.open(
        'http://www.staging.zeit.de/'
        'sport/fussball/2010-04/kaiserslautern-marcel-reif')
    assert 'id="comment-form"' in b.contents

    # testcomment = 'mein-testkommentar-{}'.format(random.random())
    testcomment = 'mein-testkommentar {}'.format(time.strftime("%c"))

    b.getForm(id='comment-form').getControl(name='comment').value = testcomment
    b.getForm(id='comment-form').getControl('Kommentar senden').click()
    assert '?cid=' in b.url
    assert testcomment in b.contents

    # logout
    b.open('https://meine.staging.zeit.de/abmelden')
    assert 'Logout erfolgreich' in b.contents


def test_endtoend_videostage_thumbnail_should_be_replaced(selenium_driver):
    driver = selenium_driver
    driver.get('http://www.staging.zeit.de/video/index')
    article = driver.find_element_by_css_selector(
        '#video-stage .video-large')
    videolink = driver.find_element_by_css_selector(
        '#video-stage .video-large figure')
    thumbnail = article.find_element_by_css_selector(
        '.video-thumbnail__media-item')
    videolink.click()
    try:
        WebDriverWait(driver, 10).until(
            expected_conditions.staleness_of(thumbnail))
        assert True
    except TimeoutException:
        assert False, 'Thumbnail not replaced by video'


def test_endtoend_video_should_load_on_video_single_page(selenium_driver):
    driver = selenium_driver
    driver.get(
        'http://www.staging.zeit.de/video/2017-02/5338993650001/argentinien-'
        'ringfoermige-sonnenfinsternis-begeistert-beobachter-in-suedamerika')

    video_visible_ec = expected_conditions.presence_of_element_located(
        (By.CLASS_NAME, 'vjs-control-bar'))

    try:
        WebDriverWait(driver, 10).until(video_visible_ec)
        assert True
    except TimeoutException:
        assert False, 'Video player not loaded'


def test_endtoend_asset_cache_header():
    response = requests.get(
        'http://www.staging.zeit.de/static/latest/css/web.site/screen.css')
    assert response.status_code == 200
    assert response.headers.get('Cache-Control', '') == 'max-age=31536000'
