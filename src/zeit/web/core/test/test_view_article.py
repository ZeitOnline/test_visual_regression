import mock
import pyramid.testing
import requests
import zeit.cms.interfaces
import zeit.web.core.view_article


def test_amp_disabled_articles_should_redirect_accordingly(testserver):
    resp = requests.get(testserver.url + '/amp/zeit-online/article/01?foo=42',
                        allow_redirects=False)
    assert resp.headers.get('Location') == (
        testserver.url + '/zeit-online/article/01?foo=42')
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


def test_advertorial_marker_is_returned_correctly():
    content = mock.Mock()
    content.advertisement_title = 'YYY'
    content.advertisement_text = 'XXX'
    content.cap_title = 'ZZZ'
    view = zeit.web.site.view_article.Article(
        content, pyramid.testing.DummyRequest())
    assert view.advertorial_marker == ('YYY', 'XXX', 'Zzz')


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
    driver.maximize_window()
    driver.get('%s/zeit-online/article/01' % testserver.url)
    body_image = driver.find_element_by_css_selector('.article__media img')
    assert body_image.get_attribute('src').endswith('desktop')


def test_url_of_single_images_is_not_suffixed_with_target_viewport(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-online/article/02' % testserver.url)
    body_image = driver.find_element_by_css_selector('.article__media img')
    source = body_image.get_attribute('src')
    assert 'bitblt' in source
    assert not source.endswith('mobile')
    assert not source.endswith('desktop')
