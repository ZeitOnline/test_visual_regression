# -*- coding: utf-8 -*-
from pyramid.httpexceptions import HTTPNotFound
from urllib2 import HTTPError
from zeit.content.article.edit.reference import Gallery, Portraitbox
from zeit.frontend import view
from zeit.frontend import view_article, view_centerpage
from zeit.frontend.block import InlineGalleryImage
from zeit.frontend.test import Browser
import mock
import pytest
import requests
import zeit.cms.interfaces


def test_breadcumb_should_produce_expected_data():
    context = mock.Mock()
    context.ressort = 'zeit-magazin'
    context.sub_ressort = 'mode-design'
    context.title = 'This is my title'

    view_article._navigation = {
        'start': (
            'Start',
            'http://www.zeit.de/index',
            'myid1'
        ),
        'zmo': (
            'ZEIT Magazin',
            'http://www.zeit.de/zeit-magazin/index',
            'myid_zmo'
        ),
        'leben': (
            'Leben',
            'http://www.zeit.de/zeit-magazin/leben/index',
            'myid2'
        ),
        'mode-design': (
            'Mode & Design',
            'http://www.zeit.de/zeit-magazin/mode-design/index',
            'myid3'
        ),
        'essen-trinken': (
            'Essen & Trinken',
            'http://www.zeit.de/zeit-magazin/essen-trinken/index',
            'myid4'
        )
    }

    article = view_article.Article(context, mock.Mock())

    l = [
        ('Start', 'http://www.zeit.de/index', 'myid1'),
        ('ZEIT Magazin', 'http://www.zeit.de/zeit-magazin/index', 'myid_zmo'),
        ('Mode & Design', 'http://www.zeit.de/zeit-magazin/mode-design/index',
            'myid3'),
        ('This is my title', ''), ]

    assert article.breadcrumb == l


def test_breadcrumb_should_be_shorter_if_ressort_or_sub_ressort_is_unknown():
    context = mock.Mock()
    context.ressort = 'zeit-magazin'
    context.sub_ressort = 'lebensartx'
    context.title = 'This is my title'

    view_article._navigation = {
        'start': (
            'Start',
            'http://www.zeit.de/index',
            'myid1'
        ),
        'zmo': (
            'ZEIT Magazin',
            'http://www.zeit.de/zeit-magazin/index',
            'myid_zmo'
        ),
        'leben': (
            'Leben',
            'http://www.zeit.de/zeit-magazin/leben/index',
            'myid2'
        ),
        'mode-design': (
            'Mode & Design',
            'http://www.zeit.de/zeit-magazin/mode-design/index',
            'myid3'
        ),
        'essen-trinken': (
            'Essen & Trinken',
            'http://www.zeit.de/zeit-magazin/essen-trinken/index',
            'myid4'
        )
    }

    article = view_article.Article(context, mock.Mock())

    l = [
        ('Start', 'http://www.zeit.de/index', 'myid1'),
        ('ZEIT Magazin', 'http://www.zeit.de/zeit-magazin/index', 'myid_zmo'),
        ('This is my title', ''), ]

    assert article.breadcrumb == l


def test_linkreach_property_should_be_set(application, app_settings):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    request = mock.Mock()
    request.registry.settings.linkreach_host = app_settings['linkreach_host']
    article_view = view_article.Article(context, request)
    article_view.request.url = 'artikel/03'
    article_view.request.traversed = ('foo',)
    article_view.request.route_url = lambda *args: ''
    assert isinstance(article_view.linkreach, dict)


def test_linkreach_property_should_fetch_correct_data(testserver,
                                                      app_settings):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    request = mock.Mock()
    request.registry.settings.linkreach_host = app_settings['linkreach_host']
    article_view = view_article.Article(context, request)
    article_view.request.url = 'foo'
    article_view.request.traversed = ('foo',)
    article_view.request.route_url = lambda *args: ''
    assert article_view.linkreach['total'] == ('1,1', 'Tsd.')


def test_header_img_should_be_first_image_of_content_blocks(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/05')
    article_view = view_article.Article(context, mock.Mock())
    url = 'http://xml.zeit.de/exampleimages/artikel/05/01.jpg'
    assert article_view.header_img.src == url


def test_article_should_have_author_box(testserver):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/artikel/autorenbox')
    article_view = view_article.Article(context, mock.Mock())
    body = zeit.content.article.edit.interfaces.IEditableBody(
        article_view.context)
    assert type(body.values()[2]) == Portraitbox


def test_header_img_should_be_none_if_we_have_a_wrong_layout(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    article_view = view_article.Article(context, mock.Mock())
    assert article_view.header_img is None


def test_header_video_should_be_first_video_of_content_blocks(application):
    vid_url = 'http://xml.zeit.de/artikel/header_video'
    context = zeit.cms.interfaces.ICMSContent(vid_url)
    article_view = view_article.Article(context, mock.Mock())
    url = 'http://brightcove.vo.llnwd.net/pd15/media/18140073001/201401/' \
        '3809/18140073001_3094832002001_Aurora-Borealis--Northern-Lights' \
        '--Time-lapses-in-Norway-Polarlichter-Der-Himmel-brennt.mp4'
    assert article_view.header_video.source == url


def test_header_video_should_be_none_if_we_have_a_wrong_layout(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    article_view = view_article.Article(context, mock.Mock())
    assert article_view.header_video is None


def test_header_elem_should_be_img_if_there_is_a_header_img(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/05')
    article_view = view_article.Article(context, mock.Mock())
    assert type(article_view.header_elem) == \
        zeit.frontend.block.HeaderImageStandard


def test_header_elem_should_be_video_if_there_is_a_header_video(application):
    xml = 'http://xml.zeit.de/artikel/header_video'
    context = zeit.cms.interfaces.ICMSContent(xml)
    article_view = view_article.Article(context, mock.Mock())
    assert type(article_view.header_elem) == zeit.frontend.block.HeaderVideo


def test_header_image_should_be_none_if_adapted_as_regular_image(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/05')
    body = zeit.content.article.edit.interfaces.IEditableBody(context)
    assert zeit.frontend.block.Image(body.values()[0]) is None


def test_image_view_returns_image_data_for_filesystem_connector(testserver):
    r = requests.get(testserver.url + '/exampleimages/artikel/01/group/01.jpg')
    assert r.headers['content-type'] == 'image/jpeg'
    assert r.text.startswith(u'\ufffd\ufffd\ufffd\ufffd\x00')


def test_inline_gallery_should_be_contained_in_body(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    body = zeit.content.article.edit.interfaces.IEditableBody(context)
    assert type(body.values()[14]) == Gallery


def test_inline_gallery_should_have_images(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    body = zeit.content.article.edit.interfaces.IEditableBody(context)
    frontend_gallery = zeit.frontend.block.InlineGallery(body.values()[14])
    assert all(type(i) is InlineGalleryImage for i in frontend_gallery.items())

    gallery_image = frontend_gallery.items()[4]
    assert gallery_image.src == \
        u'http://xml.zeit.de/galerien/bg-automesse-detroit'\
        '-2014-usa-bilder/chrysler 200 s 1-540x304.jpg'
    assert gallery_image.alt is None
    assert gallery_image.copyright == u'\xa9'


def test_article_request_should_have_body_element(testserver):
    browser = Browser('%s/artikel/05' % testserver.url)
    assert '<body itemscope itemtype="http://schema.org/WebPage">'\
        in browser.contents
    assert '</body>' in browser.contents


def test_article_request_should_have_html5_doctype(testserver):
    browser = Browser('%s/artikel/05' % testserver.url)
    assert '<!DOCTYPE html>' in browser.contents


def test_artikel05_should_have_header_image(testserver):
    browser = Browser('%s/artikel/05' % testserver.url)
    assert '<div class="article__head-wrap">' in browser.contents
    assert '<div class="scaled-image is-pixelperfect">' in browser.contents
    assert 'class="article__main-image--longform' in browser.contents


def test_column_should_have_header_image(testserver):
    browser = Browser('%s/artikel/standardkolumne-beispiel' % testserver.url)
    assert '<div class="article__column__headerimage">' in browser.contents
    assert '<div class="scaled-image">' in browser.contents
    assert '<img alt="Die ist der image sub text\n" title="Die ist der image'\
           ' sub text\n" class=" figure__media"' in browser.contents


def test_column_should_not_have_header_image(testserver):
    browser = Browser('%s/artikel/standardkolumne-ohne-bild-beispiel' %
                      testserver.url)
    assert '<div class="article__column__headerimage">' not in browser.contents


def test_health_check_should_response_and_have_status_200(testserver):
    browser = Browser('%s/health_check' % testserver.url)
    assert browser.headers['Content-Length'] == '2'
    resp = view.health_check('request')
    assert resp.status_code == 200


def test_a_404_request_should_be_from_zon_main_page(testserver):
    browser = Browser()
    browser.handleErrors = False
    with pytest.raises(HTTPError):
        browser.open('%s/this_is_a_404_page_my_dear' % testserver.url)
        assert '404 Not Found' in str(browser.headers)

    assert 'Dokument nicht gefunden' in browser.contents


def test_content_should_have_type(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/02')
    content_type = type(context).__name__.lower()
    assert content_type is not None


def test_tracking_type_is_provided(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/02')
    article_view = view_article.Article(context, mock.Mock())
    assert article_view.tracking_type == 'Artikel'


def test_artikel02_has_lebensart_ressort(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/02')
    article_view = view_article.Article(context, mock.Mock())
    assert article_view.ressort == 'lebensart'


def test_artikel02_has_leben_sub_ressort(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/02')
    article_view = view_article.Article(context, mock.Mock())
    assert article_view.sub_ressort == 'leben'


def test_artikel02_has_correct_banner_channel(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/02')
    article_view = view_article.Article(context, mock.Mock())
    assert article_view.banner_channel == 'zeitmz/leben/article'


def test_artikel05_has_rankedTagsList(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/05')
    article_view = view_article.Article(context, mock.Mock())
    assert article_view.rankedTagsList is not None
    assert article_view.rankedTagsList != ''


def test_artikel01_has_correct_authorsList(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    article_view = view_article.Article(context, mock.Mock())
    assert article_view.authorsList == 'Anne Mustermann'


def test_artikel08_has_correct_authorsList(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/08')
    article_view = view_article.Article(context, mock.Mock())
    assert article_view.authorsList == 'Anne Mustermann;Oliver Fritsch'


def test_artikel05_has_set_text_length(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/05')
    article_view = view_article.Article(context, mock.Mock())
    assert article_view.text_length is not None


def test_article05_has_correct_dates(testserver):
    # updated article
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/05')
    article_view = view_article.Article(context, mock.Mock())
    assert article_view.date_last_published_semantic.isoformat() ==\
        '2013-11-03T08:10:00.626737+01:00'
    assert article_view.date_first_released.isoformat() ==\
        '2013-10-24T08:00:00+02:00'
    assert article_view.show_article_date.isoformat() ==\
        '2013-11-03T08:10:00.626737+01:00'


def test_article03_has_correct_dates(testserver):
    # not updated article
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    article_view = view_article.Article(context, mock.Mock())
    assert article_view.date_first_released.isoformat() ==\
        '2013-07-30T17:20:50.176115+02:00'
    assert article_view.show_article_date.isoformat() ==\
        '2013-07-30T17:20:50.176115+02:00'


def test_article09_has_correct_date_formats(testserver):
    # print article, updated
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/09')
    article_view = view_article.Article(context, mock.Mock())
    assert article_view.show_date_format == 'long'
    assert article_view.show_date_format_seo == 'short'


def test_article10_has_correct_date_formats(testserver):
    # online article, updated
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/10')
    article_view = view_article.Article(context, mock.Mock())
    assert article_view.show_date_format == 'long'
    assert article_view.show_date_format_seo == 'long'


def test_article08_has_first_author(testserver):
    xml = 'http://xml.zeit.de/artikel/08'
    context = zeit.cms.interfaces.ICMSContent(xml)
    article_view = view_article.Article(context, mock.Mock())
    assert article_view.authors[0]['name'] == u'Anne Mustermann'
    assert article_view.authors[0]['suffix'] == ' und'
    assert article_view.authors[0]['prefix'] == ' von'
    assert article_view.authors[0]['location'] == ', Berlin'


def test_article08_has_second_author(testserver):
    xml = 'http://xml.zeit.de/artikel/08'
    context = zeit.cms.interfaces.ICMSContent(xml)
    article_view = view_article.Article(context, mock.Mock())
    assert article_view.authors[1]['name'] == u'Oliver Fritsch'
    assert article_view.authors[1]['suffix'] == ''
    assert article_view.authors[1]['prefix'] == ''
    assert article_view.authors[1]['location'] == ', London'


def test_article08_has_correct_genre(testserver):
    # 'ein'
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/08')
    article_view = view_article.Article(context, mock.Mock())
    assert article_view.genre == 'ein Kommentar'


def test_article09_has_correct_genre(testserver):
    # 'eine'
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/09')
    article_view = view_article.Article(context, mock.Mock())
    assert article_view.genre == 'eine Glosse'


def test_article05_has_no_genre(testserver):
    # no genre
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/05')
    article_view = view_article.Article(context, mock.Mock())
    assert article_view.genre is None


def test_article08_has_correct_source(testserver):
    # print source
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/08')
    article_view = view_article.Article(context, mock.Mock())
    assert article_view.source == 'DIE ZEIT Nr. 26/2008'


def test_article10_has_correct_source(testserver):
    # online source
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/10')
    article_view = view_article.Article(context, mock.Mock())
    assert article_view.source == 'golem.de'


def test_article03_has_empty_source(testserver):
    # zon source
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    article_view = view_article.Article(context, mock.Mock())
    assert article_view.source is None


def test_article01__has_correct_twitter_card_type(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    article_view = view_article.Article(context, mock.Mock())
    assert article_view.twitter_card_type == 'summary'


def test_article05_has_correct_twitter_card_type(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/05')
    article_view = view_article.Article(context, mock.Mock())
    assert article_view.twitter_card_type == 'summary_large_image'


def test_article01_has_correct_sharing_img_src(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    article_view = view_article.Article(context, mock.Mock())
    assert article_view.sharing_img.src == \
        'http://xml.zeit.de/exampleimages/artikel/01/group/01.jpg'


def test_article06_has_correct_sharing_img_video_still(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/06')
    article_view = view_article.Article(context, mock.Mock())
    assert article_view.sharing_img.video_still == \
        'http://brightcove.vo.llnwd.net/d21/unsecured/media/18140073001/' \
        '201401/3097/18140073001_3094729885001_7x.jpg'


def test_ArticlePage_should_throw_404_if_page_is_nan(testserver):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    page = view_article.ArticlePage(article, mock.Mock())
    page.request.registry.settings = {}
    page.request.path_info = 'article/03/seite-x'
    with pytest.raises(HTTPNotFound):
        page()


def test_ArticlePage_should_throw_404_if_no_page_in_path(testserver):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    page = view_article.ArticlePage(article, mock.Mock())
    page.request.registry.settings = {}
    page.request.path_info = 'article/03/seite-'
    with pytest.raises(HTTPNotFound):
        page()


def test_ArticlePage_should_throw_404_if_no_pages_are_exceeded(testserver):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    page = view_article.ArticlePage(article, mock.Mock())
    page.request.registry.settings = {}
    page.request.path_info = u'article/03/seite-9'
    with pytest.raises(HTTPNotFound):
        page()


def test_ArticlePage_should_not_work_if_view_name_is_seite_1(testserver):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    page = view_article.ArticlePage(article, mock.Mock())
    page.request.registry.settings = {}
    page.request.path_info = u'article/03/seite-1'
    with pytest.raises(HTTPNotFound):
        page()


def test_ArticlePage_should_work_if_pages_from_request_fit(testserver):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    page = view_article.ArticlePage(article, mock.Mock())
    page.request.registry.settings = {}
    page.request.path_info = 'article/03/seite-3'
    page()
    assert len(page.pages) == 7


def test_ArticlePage_komplett_should_show_all_pages(testserver):
    browser = Browser('%s/artikel/03/komplettansicht' % testserver.url)
    assert 'Chianti ein Comeback wirklich verdient' in browser.contents


def test_pagination_dict_should_have_correct_entries(testserver):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')

    view = view_article.ArticlePage(article, mock.Mock())
    view.request.path_info = u'article/03/seite-2'
    view.request.traversed = (u'artikel', u'03')
    view.request.route_url.return_value = '/'

    assert view.pagination['current'] == 2
    assert view.pagination['total'] == 7
    assert view.pagination['next_page_title'] == (
        u'Sogar die eckige Flasche kommt zur\xfcck')

    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    view = view_article.Article(article, mock.Mock())
    view.request.traversed = ('artikel', '03')
    view.request.route_url.return_value = '/'

    assert view.pagination['current'] == 1
    assert view.pagination['total'] == 7
    assert view.pagination['next_page_title'] == (
        u'Sogar die runde Flasche kommt zur\xfcck')


def test_pagination_next_title_should_be_in_html(testserver):
    browser = Browser('%s/artikel/03/seite-2' % testserver.url)
    assert 'Auf Seite 3' in browser.contents
    assert 'Sogar die eckige Flasche kommt' in browser.contents


def test_pagination_urls_list_should_have_correct_entries_paged_article(
        testserver):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')

    view = view_article.ArticlePage(article, mock.Mock())
    view.request.path_info = u'article/03/seite-2'
    view.request.traversed = ('artikel', '03')
    view.request.route_url.return_value = '/'

    assert view.pages_urls[0] == '/artikel/03'
    assert view.pages_urls[1] == '/artikel/03/seite-2'
    assert view.pages_urls[2] == '/artikel/03/seite-3'


def test_pagination_urls_list_should_have_correct_entries_single_article(
        testserver):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')

    view = view_article.ArticlePage(article, mock.Mock())
    view.request.path_info = u'article/01'
    view.request.traversed = (u'artikel', u'01')
    view.request.route_url.return_value = '/'

    assert view.pages_urls[0] == '/artikel/01'
    assert len(view.pages_urls) == 1


def test_pagination_next_page_url_is_working(testserver):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    view = view_article.Article(article, mock.Mock())
    view.request.traversed = (u'artikel', u'03')
    view.request.route_url.return_value = '/'

    assert view.pagination['next_page_url'] == '/artikel/03/seite-2'


def test_pagination_next_page_url_on_last_page_is_none(testserver):
    browser = Browser('%s/artikel/03/seite-7' % testserver.url)
    content = '<span class="icon-pagination-next">Vor</span>'

    assert content in browser.contents


def test_pagination_prev_page_url_is_working(testserver):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')

    view = view_article.ArticlePage(article, mock.Mock())
    view.request.path_info = u'article/03/seite-2'
    view.request.traversed = (u'artikel', u'03')
    view.request.route_url.return_value = '/'

    assert view.pagination['prev_page_url'] == u'/artikel/03'


def test_pagination_prev_page_url_on_first_page_is_none(testserver):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    view = view_article.Article(article, mock.Mock())
    view.request.traversed = ('artikel', '03')
    view.request.route_url.return_value = '/'
    assert view.pagination['prev_page_url'] is None


def test_article09_should_have_a_nextread(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/09')
    view = view_article.Article(context, mock.Mock())
    assert view.nextread is not None


def test_article01_should_not_have_a_nextread(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    view = view_article.Article(context, mock.Mock())
    assert view.nextread is None


def test_cp_teaser_with_comments_should_get_comments_count(testserver):
    request = mock.Mock()
    request.registry.settings.node_comment_statistics = \
        'data/node-comment-statistics.xml'
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo')
    view = view_centerpage.Centerpage(cp, request)
    view()  # trigger __call__ method
    comment_count = view.teaser_get_commentcount(
        'http://xml.zeit.de/centerpage/article_image_asset')
    assert comment_count == '22'
    # For teaser uniquId with no entry in node-comment-statistics
    # teaser_get_commentcount should return None
    comment_count = view.teaser_get_commentcount(
        'http://xml.zeit.de/centerpage/article_image_assetXXX')
    assert comment_count is None


def test_caching_headers_should_be_set(testserver):
    browser = Browser('%s/artikel/05' % testserver.url)
    assert browser.headers['cache-control'] == 'max-age=300'


def test_iqd_mobile_settings_are_filled(testserver):
    # tested just as examlpe for an article here, all possible combinations
    # are tested in test_banner.py integration tests
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    view = view_article.Article(article, mock.Mock())
    assert view.iqd_mobile_settings.get('top') == '445612'
    assert view.iqd_mobile_settings.get('middle') == '445612'
    assert view.iqd_mobile_settings.get('bottom') == '445612'

