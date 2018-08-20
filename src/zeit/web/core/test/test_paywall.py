import requests

import zeit.cms.content.metadata

import zeit.web.core.application


def test_adblocker_header_should_be_true_by_default(testserver):
    zeit.web.core.application.FEATURE_TOGGLES.set('c1_adblocker_blocker')
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/simple')
    assert context.hide_adblocker_notification is None  # Ensure test case

    url = testserver.url + '/zeit-online/article/simple'
    assert requests.head(url).headers.get(
        'C1-Track-Adblocker-Targeting') == 'true'


def test_adblocker_header_should_be_false_when_disabled_via_property(
        testserver, monkeypatch):
    zeit.web.core.application.FEATURE_TOGGLES.set('c1_adblocker_blocker')
    monkeypatch.setattr(
        zeit.cms.content.metadata.CommonMetadata,
        'hide_adblocker_notification', True)
    zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/simple')

    url = testserver.url + '/zeit-online/article/simple'
    assert requests.head(url).headers.get(
        'C1-Track-Adblocker-Targeting') == 'false'
