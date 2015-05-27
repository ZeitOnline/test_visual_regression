# -*- coding: utf-8 -*-
import mock
import pytest
import requests
import urllib2

import zeit.web.core.date
import zeit.web.core.interfaces
import zeit.web.magazin.view
import zeit.web.magazin.view_article
import zeit.web.magazin.view_centerpage
import zeit.web.site.view
import zeit.web.site.view_article
import zeit.web.site.view_centerpage


@pytest.fixture
def mock_ad_view(application):
    class MockAdView(zeit.web.core.view.Base):
        def __init__(
                self, type, ressort,
                sub_ressort, is_hp=False, banner_id=None, serienname='',
                product_id=None):
            self.type = type
            self.ressort = ressort
            self.sub_ressort = sub_ressort
            self.is_hp = is_hp
            self.product_id = product_id
            self.serie = serienname
            context = mock.Mock()
            context.banner_id = banner_id
            self.context = context

    return MockAdView


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
    monkeypatch.setattr(zeit.web.core.date, 'get_base_date', lambda *_: now)

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


def test_breaking_news_should_be_provided(application):
    view = zeit.web.core.view.Base(None, None)
    assert zeit.web.core.interfaces.IBreakingNews.providedBy(
        view.breaking_news)


def test_unpublished_breaking_news_should_be_detected(application):
    view = zeit.web.core.view.Base(None, None)
    assert view.breaking_news.published is False


def test_published_breaking_news_should_be_detected(application, monkeypatch):
    monkeypatch.setattr(
        zeit.workflow.workflow.ContentWorkflow, 'published', True)
    view = zeit.web.core.view.Base(None, None)
    assert view.breaking_news.published is True


def test_missing_breaking_news_should_eval_to_false(
        application, app_settings, ephemeral_settings):
    app_settings['breaking_news'] = 'moep'
    ephemeral_settings(app_settings)
    view = zeit.web.core.view.Base(None, None)
    assert view.breaking_news.published is False


def test_adcontroller_handle_return_value(mock_ad_view):
    assert mock_ad_view('centerpage', 'politik', ''
                        ).adcontroller_handle == 'index'
    assert mock_ad_view('centerpage', 'zeit-magazin', ''
                        ).adcontroller_handle == 'index'
    assert mock_ad_view('centerpage', 'homepage', '', is_hp=True
                        ).adcontroller_handle == 'homepage'
    assert mock_ad_view('centerpage', 'politik', 'deutschland'
                        ).adcontroller_handle == 'centerpage'
    assert mock_ad_view('article', 'politik', 'deutschland'
                        ).adcontroller_handle == 'artikel'
    assert mock_ad_view('video', 'politik', 'deutschland'
                        ).adcontroller_handle == 'video_artikel'
    assert mock_ad_view('quiz', 'politik', 'deutschland'
                        ).adcontroller_handle == 'quiz'


def test_banner_channel_mapping_should_apply_first_rule(mock_ad_view):
    assert mock_ad_view(
        'centerpage', 'angebote', '',
        banner_id='mein/ad/code').banner_channel == 'mein/ad/code/centerpage'


def test_banner_channel_mapping_should_apply_second_rule(mock_ad_view):
    assert mock_ad_view('centerpage', 'angebote', '',
                        serienname='meh').banner_channel == (
        'angebote/meh/centerpage')
    assert mock_ad_view('centerpage', 'angebote', '',
                        serienname='a k').banner_channel == (
        'angebote/a_k/centerpage')


def test_banner_channel_mapping_should_apply_third_rule(mock_ad_view):
    assert mock_ad_view('centerpage', 'zeit-magazin',
                        'irgendwas').banner_channel == (
        'zeitmz/irgendwas/centerpage')
    assert mock_ad_view('centerpage', 'lebensart',
                        '').banner_channel == 'zeitmz/centerpage'
    assert mock_ad_view(
        'centerpage', 'mobilitaet', '').banner_channel == 'auto/centerpage'
    assert mock_ad_view(
        'centerpage', 'ranking', '').banner_channel == 'studium/centerpage'
    assert mock_ad_view(
        'centerpage', 'sport',
        '', product_id='news').banner_channel == 'news/centerpage'
    assert mock_ad_view(
        'centerpage', 'politk',
        '', product_id='sid').banner_channel == 'sid/centerpage'
    assert mock_ad_view(
        'article', 'foto', '').banner_channel == 'kultur/article'
    assert mock_ad_view(
        'article', 'wirtschaft', 'geld',
        serienname='geldspezial').banner_channel == 'geldspezial/article'
    assert mock_ad_view(
        'centerpage',
        'sport',
        'zeit wissen').banner_channel == 'wissen/zeit_wissen/centerpage'
    assert mock_ad_view(
        'centerpage',
        'sport',
        'zeit campus').banner_channel == 'wissen/zeit_campus/centerpage'
    assert mock_ad_view('centerpage', 'sport',
                        'zeit geschichte').banner_channel == (
        'wissen/zeit_geschichte/centerpage')
    assert mock_ad_view('centerpage', 'sport',
                        'das wissen dieser welt').banner_channel == (
        'wissen/bildungskanon/centerpage')
    assert mock_ad_view(
        'centerpage', 'wissen', '', serienname="spiele").banner_channel == (
        'spiele/centerpage')
    assert mock_ad_view(
        'centerpage',
        'campus',
        'irgendwas').banner_channel == 'studium/irgendwas/centerpage'
    assert mock_ad_view(
        'centerpage', 'wissen', '', serienname="reise").banner_channel == (
        'reisen/centerpage')
    assert mock_ad_view('centerpage', 'kultur',
                        'computer').banner_channel == 'digital/centerpage'
    assert mock_ad_view(
        'centerpage', 'technik', '').banner_channel == 'digital/centerpage'


def test_banner_channel_mapping_should_apply_fourthandfitfth(mock_ad_view):
    assert mock_ad_view(
        'centerpage', 'politik', '').banner_channel == 'politik/centerpage'
    assert mock_ad_view(
        'centerpage', 'pol', 'deu').banner_channel == 'pol/deu/centerpage'


def test_banner_channel_mapping_should_apply_last_rule(mock_ad_view):
    assert mock_ad_view(
        'centerpage', '', '').banner_channel == 'vermischtes/centerpage'


def test_adcontroller_values_are_correctly_returned(mock_ad_view):
    zw_code = [('$handle', 'centerpage'), ('level2', 'wissen'),
               ('level3', 'zeit_wissen'), ('$autoSizeFrames', True),
               ('keywords', ''), ('tma', '')]
    zw_test = mock_ad_view(
        'centerpage', 'sport', 'zeit wissen').adcontroller_values
    assert zw_code == zw_test
    zmz_code = [('$handle', 'index'), ('level2', 'zeitmz'),
                ('level3', 'irgendwas'), ('$autoSizeFrames', True),
                ('keywords', ''), ('tma', '')]
    zmz_test = mock_ad_view(
        'centerpage', 'zeit-magazin', 'irgendwas').adcontroller_values
    assert zmz_code == zmz_test


def test_centerpage_should_have_manual_seo_pagetitle(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/index')
    view = zeit.web.magazin.view_centerpage.Centerpage(context, mock.Mock())
    assert view.pagetitle == u'My Test SEO - ZEITmagazin ONLINE'


def test_centerpage_should_have_generated_seo_pagetitle(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/centerpage/lebensart-3')
    view = zeit.web.magazin.view_centerpage.Centerpage(context, mock.Mock())
    assert view.pagetitle == u'ZMO CP: ZMO | ZEITmagazin'


def test_article_should_have_postfixed_seo_pagetitle(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/artikel/06')
    view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert view.pagetitle == (u'Friedhof Hamburg-Ohlsdorf: '
                              'Im Schnabel des Graureihers | ZEITmagazin')


def test_homepage_should_have_unpostfixed_seo_pagetitle(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/index')
    view = zeit.web.site.view_centerpage.Centerpage(context, mock.Mock())
    assert view.pagetitle == u'ZON title'


def test_centerpage_should_have_manual_seo_pagedescription(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/index')
    view = zeit.web.magazin.view_centerpage.Centerpage(context, mock.Mock())
    assert view.pagedescription == (u'My Test SEO - ZEITmagazin ONLINE ist '
                                    'die emotionale Seite von ZEIT ONLINE.')


def test_centerpage_should_have_subtitle_seo_pagedesciption(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/centerpage/lebensart-3')
    view = zeit.web.magazin.view_centerpage.Centerpage(context, mock.Mock())
    assert view.pagedescription == u'ZMO CP'


def test_centerpage_should_have_default_seo_pagedescription(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/index')
    view = zeit.web.magazin.view_centerpage.Centerpage(context, mock.Mock())
    assert view.pagedescription == zeit.web.magazin.view.Base.seo_title_default
