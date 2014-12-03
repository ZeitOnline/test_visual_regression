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
