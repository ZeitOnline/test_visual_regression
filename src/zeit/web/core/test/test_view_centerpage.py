import zeit.cms.interfaces

import zeit.web.core.view_centerpage


def test_centerpage_should_return_jsonp_with_timestamp_if_released(
        testserver, testbrowser):
    # published page returns its pubdate
    browser = testbrowser(
        '%s/zeit-online/main-teaser-setup/json_update_time?callback=123'
        % testserver.url)
    pubstring = (
        '123({"last_published_semantic": '
        '"2014-11-18T12:18:27.293179+00:00", '
        '"last_published": "2014-11-18T12:18:27.293179+00:00"})')
    assert browser.headers.type == 'application/javascript'
    assert pubstring == browser.contents


def test_centerpage_should_return_jsonp_with_timestamp_if_not_released(
        testserver, testbrowser):
    # published page returns empty string
    browser = testbrowser(
        '%s/zeit-online/teaser-serie-setup/json_update_time?callback=123'
        % testserver.url)
    pubstring = '123({"last_published_semantic": "", "last_published": ""})'
    assert browser.headers.type == 'application/javascript'
    assert pubstring == browser.contents


def test_centerpage_should_return_json_without_callback(
        testserver, testbrowser):
    # pure json when url has no callback
    browser = testbrowser(
        '%s/zeit-online/main-teaser-setup/json_update_time' % testserver.url)
    assert browser.headers.type == 'application/json'
    assert browser.json == {
        u'last_published_semantic': u'2014-11-18T12:18:27.293179+00:00',
        u'last_published': u'2014-11-18T12:18:27.293179+00:00'}


def test_centerpage_should_aggregate_all_teasers_correctly(
        application, dummy_request):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo-2')
    items = list(zeit.web.core.view_centerpage.Centerpage(cp, dummy_request))
    assert items[0].uniqueId == (
        'http://xml.zeit.de/zeit-magazin/test-cp/essen-geniessen-spargel-lamm')
    assert len(items) == 13


def test_centerpage_should_collect_teaser_counts_from_community(
        application, dummy_request, mockserver_factory):
    cp_counts = """<?xml version="1.0" encoding="UTF-8"?>
    <nodes>
         <node comment_count="129"
               url="/zeit-magazin/test-cp/essen-geniessen-spargel-lamm"/>
    </nodes>
    """
    mockserver_factory(cp_counts)
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo-2')
    view = zeit.web.core.view_centerpage.Centerpage(cp, dummy_request)
    path, count = view.comment_counts.items()[0]
    assert '/zeit-magazin/test-cp/essen-geniessen-spargel-lamm' in path
    assert count == '129'
