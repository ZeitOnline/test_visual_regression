import pytest
import requests
import urllib2

import zeit.web.core.date
import zeit.web.core.interfaces
import zeit.web.site.view


def test_json_delta_time_from_date_should_return_null(testserver,
                                                      testbrowser):
    browser = testbrowser(
        '{}/json/delta_time?'
        'date=2014-10-14T09%3A06%3A45.950590%2B00%3A00'
        '&base_date=2014-10-15T10%3A06%3A45.950590%2B00%3A00'.format(
            testserver.url))
    assert browser.contents == (
        '{"delta_time": {"time": null}}')


def test_json_delta_time_from_date_should_return_delta_time(testserver,
                                                            testbrowser):
    browser = testbrowser(
        '{}/json/delta_time?'
        'date=2014-10-14T09%3A06%3A45.950590%2B00%3A00'
        '&base_date=2014-10-14T10%3A36%3A45.950590%2B00%3A00'.format(
            testserver.url))
    assert browser.contents == (
        '{"delta_time": {"time": "vor 1 Stunde"}}')


def test_json_delta_time_from_date_should_fallback_to_now_for_base_date(
        testserver, testbrowser):
    browser = testbrowser(
        '{}/json/delta_time?'
        'date=2014-10-15T10%3A06%3A45.950590%2B00%3A00'.format(
            testserver.url))
    assert browser.contents is not None
    assert browser.contents != ''


def test_json_delta_time_from_date_should_return_http_error_on_missing_params(
        testserver, testbrowser):
    with pytest.raises(urllib2.HTTPError):
        testbrowser('{}/json/delta_time'.format(testserver.url))


def test_json_delta_time_from_unique_id_should_return_delta_time(testserver,
                                                                 testbrowser,
                                                                 monkeypatch):
    now = zeit.web.core.date.parse_date('2014-10-15T16:53:59.780412+00:00')
    monkeypatch.setattr(zeit.web.core.date, 'utcnow', lambda: now)

    browser = testbrowser(
        '{}/json/delta_time?'
        'unique_id=http://xml.zeit.de/zeit-online/main-teaser-setup'.format(
            testserver.url))
    assert browser.contents == (
        '{"delta_time": ['
        '{"http://xml.zeit.de/zeit-online/cp-content/article-01": '
        '{"time": "vor 2 Stunden"}}, '
        '{"http://xml.zeit.de/zeit-online/cp-content/article-02": '
        '{"time": "vor 2 Stunden"}}]}')


def test_json_delta_time_from_unique_id_should_return_http_error_on_false_uid(
        testserver, testbrowser):
    with pytest.raises(urllib2.HTTPError):
        testbrowser('{}/json/delta_time?unique_id=foo'.format(testserver.url))


def test_json_delta_time_from_unique_id_should_return_http_error_on_article(
        testserver, testbrowser):
    with pytest.raises(urllib2.HTTPError):
        testbrowser('{}/json/delta_time?unique_id='
                    'http://xml.zeit.de/artikel/01'.format(testserver.url))


def test_json_delta_time_from_unique_id_should_use_custom_base_time(
        testserver, testbrowser):
    browser = testbrowser(
        '{}/json/delta_time?base_date=2014-10-15T16%3A06%3A45.95%2B00%3A00&'
        'unique_id=http://xml.zeit.de/zeit-online/main-teaser-setup'.format(
            testserver.url))
    assert 'vor 1 Stunde' in browser.contents


def test_http_header_should_contain_c1_header_fields(testserver, testbrowser):
    c1_track_doc_type = requests.head(
        testserver.url + '/zeit-magazin/index').headers['c1-track-doc-type']
    c1_track_channel = requests.head(
        testserver.url + '/zeit-magazin/index').headers['c1-track-channel']
    c1_track_kicker = requests.head(
        testserver.url + '/artikel/03').headers['c1-track-kicker']
    assert c1_track_doc_type == 'Centerpage'
    assert c1_track_channel == 'Lebensart'
    assert c1_track_kicker == 'Kolumne Die Ausleser'


def test_http_header_should_not_contain_empty_fields(
        testserver, testbrowser):
    with pytest.raises(KeyError):
        requests.head(
            testserver.url +
            '/zeit-magazin/index').headers['c1-track-sub-channel']


def test_text_file_content_should_be_rendered(testserver, testbrowser):
    browser = testbrowser('{}/text/dummy'.format(testserver.url))
    assert browser.contents == 'zeit.web\n'


def test_inline_gallery_should_be_contained_in_body(testserver, testbrowser):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    body = zeit.content.article.edit.interfaces.IEditableBody(context)
    assert (
        isinstance(body.values()[14],
                   zeit.content.article.edit.reference.Gallery))


def test_inline_gallery_should_have_images(testserver, testbrowser):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    body = zeit.content.article.edit.interfaces.IEditableBody(context)
    gallery = zeit.web.core.block.IFrontendBlock(body.values()[14])
    assert all(
        zeit.web.core.gallery.IGalleryImage.providedBy(i)
        for i in gallery.itervalues())

    image = gallery.values()[4]
    assert image.src == (
        u'http://xml.zeit.de/galerien/bg-automesse-detroit'
        '-2014-usa-bilder/chrysler 200 s 1-540x304.jpg')
    assert image.alt is None
    assert image.copyright[0][0] == u'\xa9'


def test_unpublished_breaking_news_should_be_detected(application):
    assert zeit.web.core.view.check_breaking_news() is False


def test_published_breaking_news_should_be_detected(application, monkeypatch):
    monkeypatch.setattr(
        zeit.workflow.workflow.ContentWorkflow, 'published', True)
    assert zeit.web.core.view.check_breaking_news() is True


def test_missing_breaking_news_should_eval_to_false(
        application, app_settings, ephemeral_settings):
    app_settings['breaking_news'] = 'moep'
    ephemeral_settings(app_settings)
    assert zeit.web.core.view.check_breaking_news() is False
