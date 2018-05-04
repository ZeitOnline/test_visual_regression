import pytest

import zeit.web.core.application


@pytest.mark.parametrize('url', [
    '/zeit-online/video/3537342483001',
    '/zeit-online/article/video'
])
def test_babator_is_shown_on_video_pages(testbrowser, url):
    zeit.web.core.application.FEATURE_TOGGLES.set('babator')
    browser = testbrowser(url)
    assert browser.cssselect('script[src*="babator.com"]')


@pytest.mark.parametrize('url', [
    '/zeit-online/article/simple',
    '/zeit-online/article/video-expired'
])
def test_babator_is_not_shown_on_other_pages(testbrowser, url):
    zeit.web.core.application.FEATURE_TOGGLES.set('babator')
    browser = testbrowser(url)
    assert not browser.cssselect('script[src*="babator.com"]')


@pytest.mark.parametrize('url', [
    '/zeit-online/video/3537342483001',
    '/zeit-online/article/video'
])
def test_babator_can_be_toggled_off(testbrowser, url):
    zeit.web.core.application.FEATURE_TOGGLES.unset('babator')
    browser = testbrowser(url)
    assert not browser.cssselect('script[src*="babator.com"]')
