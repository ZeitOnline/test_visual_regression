import mock
import pyramid.testing
import pytest
import requests
import zope.component

from zeit.cms.checkout.helper import checked_out
import zeit.cms.interfaces

import zeit.web.core.view_article

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


def test_amp_disabled_articles_should_redirect_accordingly(testserver):
    resp = requests.get(testserver.url + '/amp/zeit-online/article/01?foo=42',
                        allow_redirects=False)
    assert resp.headers.get('Location') == (
        testserver.url + '/zeit-online/article/01?foo=42')
    assert resp.status_code == 302


def test_amp_disabled_specialized_articles_should_redirect_accordingly(
        testserver, workingcopy):
    with checked_out(zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/zeit-online/article/liveblog3')) as co:
        co.is_amp = False
    resp = requests.get(
        testserver.url + '/amp/zeit-online/article/liveblog3?foo=42',
        allow_redirects=False)
    assert resp.headers.get('Location') == (
        testserver.url + '/zeit-online/article/liveblog3?foo=42')
    assert resp.status_code == 302


def test_article_tags_template_renders_rel_attribute(
        tplbrowser, dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/tags')
    view = zeit.web.core.view_article.Article(context, dummy_request)
    browser = tplbrowser(
        'zeit.web.core:templates/inc/article/tags.html',
        view=view, request=dummy_request)
    tags = browser.cssselect('a.article-tags__link')
    for tag in tags:
        assert tag.get('rel') == 'tag'


def test_adc_keywords_are_sanitized_correctly(selenium_driver, testserver):
    driver = selenium_driver
    # avoid "diuquilon", which is added by JS for specific screen sizes
    driver.set_window_size(1200, 800)
    zeit.web.core.application.FEATURE_TOGGLES.set('third_party_modules', 'iqd')
    driver.get('%s/zeit-online/article/tags' % testserver.url)
    assert ('zeitonline,mailand,claudioabbado,johannsebastianbach,oper,'
            'opernhaus,10slze42foo' == driver.execute_script(
                'return adcSiteInfo.keywords'))


def test_advertorial_marker_is_returned_correctly():
    content = mock.Mock()
    content.advertisement_title = 'YYY'
    content.advertisement_text = 'XXX'
    content.cap_title = 'ZZZ'
    view = zeit.web.site.view_article.Article(
        content, pyramid.testing.DummyRequest())
    assert view.advertorial_marker == ('YYY', 'XXX', 'Zzz')


def test_liveblog_article_renders_if_liveblog_api_backend_is_down(testbrowser):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    conf['liveblog_api_url_v3'] = 'http://unavailable//api/blogs'
    conf['liveblog_api_auth_url_v3'] = 'http://unavailable/auth'
    browser = testbrowser('/zeit-online/article/liveblog3')
    assert browser.cssselect('body')
    assert browser.cssselect('div#navigation')
    assert browser.cssselect('main#main')


def test_liveblog_article_renders_if_liveblog_content_backend_is_down(testbrowser):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    conf['liveblog_api_url_v3'] = 'http://unavailable//api/blogs'
    conf['liveblog_api_auth_url_v3'] = 'http://unavailable/auth'
    conf['liveblog_backend_url_v3'] = 'http://unavailable/v3'
    browser = testbrowser('/zeit-online/article/liveblog3')
    assert browser.cssselect('body')
    assert browser.cssselect('div#navigation')
    assert browser.cssselect('main#main')


def test_url_of_image_groups_is_suffixed_with_mobile_on_small_browser_size(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.set_window_size(320, 480)
    driver.get('%s/zeit-online/article/01' % testserver.url)
    body_image = driver.find_element_by_css_selector('.article__media img')
    assert body_image.get_attribute('src').endswith('mobile')


def test_url_of_image_groups_is_suffixed_with_desktop_on_big_browser_size(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.set_window_size(1280, 860)
    driver.get('%s/zeit-online/article/01' % testserver.url)
    try:
        body_image = WebDriverWait(driver, 2).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '.article__media img')))
        assert body_image.get_attribute('src').endswith('desktop')
    except TimeoutException:
        assert False


def test_app_user_feedback_is_working(selenium_driver, testserver):
    driver = selenium_driver
    driver.set_window_size(375, 667)
    script = 'return window.Zeit.appUserFeedback("app-rating")'
    driver.get(
        '{}/arbeit/article/simple?app-content'.format(
            testserver.url))
    driver.execute_script(script)
    try:
        WebDriverWait(driver, 2).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '.app-feedback')))
        assert True
    except TimeoutException:
        assert False, 'appUserFeedback message not shown within 2 seconds'


@pytest.mark.parametrize(
    'content', [
        ('/zeit-online/article/fischer',
         '.column-heading__media-item',
         'Julia Zange'),
        ('/zeit-online/article/authorbox',
         '.authorbox__media-item',
         'Jochen Wegner'),
        ('/zeit-online/centerpage/register',
         '.teaser-fullwidth-column__media-item',
         'Julia Zange'),
        ('/arbeit/article/column',
         '.article-header-column__media-item',
         'Julia Zange'),
        ('/campus/article/column',
         '.article-header__media-item',
         'Thomas Fischer')
    ])
def test_author_images_should_have_name_as_alt(content, testbrowser):
    browser = testbrowser(content[0])
    browser.cssselect(content[1])[0].get('alt') == content[2]
