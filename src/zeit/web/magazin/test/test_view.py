# -*- coding: utf-8 -*-
import pkg_resources
import urllib2

import lxml.html
import mock
import pyramid.httpexceptions
import pyramid.response
import pyramid.testing
import pytest
import requests

import zeit.cms.interfaces
import zeit.content.article.edit.reference

import zeit.web.core
import zeit.web.core.gallery
import zeit.web.core.view
import zeit.web.magazin.view_article


def test_base_view_produces_acceptable_return_type(application, dummy_request):
    class BaseView(zeit.web.core.view.Base):

        """This view class does not implement a __call__ method."""

        pass
    content = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    obj = BaseView(content, dummy_request)
    assert hasattr(obj(), '__iter__'), 'BaseView returns an iterable type.'


def test_response_view_produces_acceptable_return_type():
    class ResponseView(zeit.web.core.view.Base):

        """This view class explicitly returns a pyramid response."""

        def __call__(self):
            return pyramid.response.Response('OK', 200)

    obj = ResponseView(mock.Mock(), mock.Mock())
    assert isinstance(obj(), pyramid.response.Response), (
        'ResponseView retains its return type.')


def test_dict_view_produces_acceptable_return_value():
    class DictView(zeit.web.core.view.Base):

        """This view class returns a dictionary."""

        def __call__(self):
            return {'bar': 1}

    obj = DictView(mock.Mock(), mock.Mock())
    assert obj() == {'bar': 1}, 'DictView retains its return value.'


def test_breadcumb_should_produce_expected_data():
    context = mock.Mock()
    context.ressort = 'zeit-magazin'
    context.sub_ressort = 'mode-design'
    context.title = 'This is my title'

    request = mock.Mock()
    request.route_url.return_value = 'http://foo.bar/'

    article = zeit.web.magazin.view_article.Article(context, request)

    crumbs = [
        ('Start', 'http://foo.bar/index'),
        ('ZEIT Magazin', 'http://foo.bar/zeit-magazin/index'),
        ('Mode & Design', 'http://foo.bar/zeit-magazin/mode-design/index'),
        ('This is my title', '')
    ]

    assert article.breadcrumb == crumbs


def test_breadcrumb_should_be_shorter_if_ressort_or_sub_ressort_is_unknown():
    context = mock.Mock()
    context.ressort = 'zeit-magazin'
    context.sub_ressort = 'lebensartx'
    context.title = 'This is my title'

    request = mock.Mock()
    request.route_url.return_value = 'http://foo.bar/'

    article = zeit.web.magazin.view_article.Article(context, request)

    crumbs = [
        ('Start', 'http://foo.bar/index'),
        ('ZEIT Magazin', 'http://foo.bar/zeit-magazin/index'),
        ('This is my title', '')
    ]

    assert article.breadcrumb == crumbs


def test_linkreach_property_should_be_set(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    article_view.request.url = 'index'
    article_view.request.traversed = ('index',)
    article_view.request.route_url = lambda *args: ''
    assert isinstance(article_view.linkreach, dict)


def test_linkreach_property_should_fetch_correct_data(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    article_view.request.url = 'index'
    article_view.request.traversed = ('index',)
    article_view.request.route_url = lambda *args: ''
    assert article_view.linkreach['total'] == 92


def test_header_img_should_be_first_image_of_content_blocks(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/05')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    url = 'http://xml.zeit.de/exampleimages/artikel/05/01.jpg'
    assert article_view.header_img.src == url


def test_article_should_have_author_box(testserver, testbrowser):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/artikel/autorenbox')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    body = zeit.content.article.edit.interfaces.IEditableBody(
        article_view.context)
    assert isinstance(body.values()[2], (
        zeit.content.article.edit.reference.Portraitbox))


def test_header_img_should_be_none_if_we_have_a_wrong_layout(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert article_view.header_img is None


def test_header_video_should_be_first_video_of_content_blocks(application):
    vid_url = 'http://xml.zeit.de/artikel/header_video'
    context = zeit.cms.interfaces.ICMSContent(vid_url)
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    url = ('http://brightcove.vo.llnwd.net/pd15/media/18140073001/201401/'
           '3809/18140073001_3094832002001_Aurora-Borealis--Northern-Lights'
           '--Time-lapses-in-Norway-Polarlichter-Der-Himmel-brennt.mp4')
    assert article_view.header_video.highest_rendition == url


def test_header_video_should_be_none_if_we_have_a_wrong_layout(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert article_view.header_video is None


def test_header_elem_should_be_img_if_there_is_a_header_img(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/05')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert isinstance(article_view.header_elem, (
        zeit.web.core.block.HeaderImageStandard))


def test_header_elem_should_be_video_if_there_is_a_header_video(application):
    xml = 'http://xml.zeit.de/artikel/header_video'
    context = zeit.cms.interfaces.ICMSContent(xml)
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert isinstance(
        article_view.header_elem, zeit.web.core.block.HeaderVideo)


def test_header_image_should_be_none_if_adapted_as_regular_image(
        testserver, testbrowser):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/05')
    body = zeit.content.article.edit.interfaces.IEditableBody(context)
    assert zeit.web.core.block.Image(body.values()[0]) is None


def test_image_view_returns_image_data_for_filesystem_connector(
        testserver, testbrowser):
    r = requests.get(testserver.url +
                     '/exampleimages/artikel/01/'
                     'schoppenstube/schoppenstube-540x304.jpg')
    assert r.headers['content-type'] == 'image/jpeg'
    assert r.text.startswith(u'\ufffd\ufffd\ufffd\ufffd\x00')


def test_footer_should_have_expected_markup(testserver, testbrowser):
    browser = testbrowser('%s/artikel/01' % testserver.url)
    elem = browser.cssselect('footer.main-footer')[0]
    # assert normal markup
    expect = '<footer class="main-footer">'\
        '<div class="main-footer__box is-constrained is-centered">'\
        '<div class="main-footer__logo icon-logo-zmo-small"></div>'\
        '<div class="main-footer__links"><div><ul><li>VERLAG</li>'\
        '<li><a href="http://www.zeit-verlagsgruppe.de/anzeigen/">'\
        'Mediadaten</a></li><li><a href="http://www.zeit-verlagsgruppe.de'\
        '/marken-und-produkte/geschaeftskunden/artikel-nachrucke/">'\
        'Rechte &amp; Lizenzen</a></li>'\
        '</ul></div><div><ul><li><a class="js-toggle-copyrights">'\
        'Bildrechte</a></li>'\
        '<li><a href="{0}/hilfe/datenschutz">'\
        'Datenschutz</a></li>'\
        '<li><a href="'\
        'http://www.iqm.de/Medien/Online/nutzungsbasierte_'\
        'onlinewerbung.html">Cookies</a></li>'\
        '<li><a href="{0}/administratives/'\
        'agb-kommentare-artikel">AGB</a></li>'\
        '<li><a href="{0}/impressum/index">Impressum</a></li>'\
        '<li><a href="{0}/hilfe/hilfe">Hilfe/ Kontakt</a></li>'\
        '</ul></div></div></div></footer>'.format(testserver.url)
    got = [s.strip() for s in lxml.html.tostring(elem).splitlines()]
    got = "".join(got)
    assert expect == got


def test_article_request_should_have_body_element(testserver, testbrowser):
    browser = testbrowser('%s/artikel/05' % testserver.url)
    assert ('<body itemscope itemtype='
            '"http://schema.org/WebPage"') in browser.contents
    assert '</body>' in browser.contents


def test_article_request_should_have_html5_doctype(testserver, testbrowser):
    browser = testbrowser('%s/artikel/05' % testserver.url)
    assert '<!DOCTYPE html>' in browser.contents


def test_artikel05_should_have_header_image(testserver, testbrowser):
    browser = testbrowser('%s/artikel/05' % testserver.url)
    assert '<div class="article__head-wrap">' in browser.contents
    assert ('<div class="scaled-image is-pixelperfect'
            ' article__head-image">') in browser.contents
    assert 'class=" figure__media' in browser.contents


def test_column_should_have_header_image(testserver, testbrowser):
    browser = testbrowser(
        '%s/artikel/standardkolumne-beispiel' % testserver.url)
    assert '<div class="article__column__headerimage">' in browser.contents
    assert '<div class="scaled-image">' in browser.contents
    assert ('<img alt="Die ist der image sub text" title="Die ist der image'
            ' sub text" class=" figure__media"') in browser.contents


def test_column_should_not_have_header_image(testserver, testbrowser):
    browser = testbrowser(
        '%s/artikel/standardkolumne-ohne-bild-beispiel' % testserver.url)
    assert '<div class="article__column__headerimage">' not in browser.contents


def test_health_check_should_response_and_have_status_200(
        testserver, testbrowser):
    browser = testbrowser('%s/health_check' % testserver.url)
    assert browser.headers['Content-Length'] == '2'
    resp = zeit.web.core.view.health_check('request')
    assert resp.status_code == 200


def test_a_404_request_should_be_from_zon_main_page(testserver, testbrowser):
    browser = testbrowser()
    browser.handleErrors = False
    with pytest.raises(urllib2.HTTPError):
        browser.open('%s/this_is_a_404_page_my_dear' % testserver.url)
        assert '404 Not Found' in str(browser.headers)

    assert 'Dokument nicht gefunden' in browser.contents


def test_content_should_have_type(testserver, testbrowser):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/02')
    content_type = type(context).__name__.lower()
    assert content_type is not None


def test_tracking_type_is_provided(testserver, testbrowser):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/02')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert article_view.tracking_type == 'article'


def test_artikel02_has_lebensart_ressort(testserver, testbrowser):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/02')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert article_view.ressort == 'lebensart'


def test_artikel02_has_leben_sub_ressort(testserver, testbrowser):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/02')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert article_view.sub_ressort == 'leben'


def test_artikel02_has_correct_banner_channel(testserver, testbrowser):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/02')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert article_view.banner_channel == 'zeitmz/leben/article'


def test_artikel05_has_meta_keywords(testserver, testbrowser):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/05')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert article_view.meta_keywords == ['Sterben', 'Tod', 'Bestattung']


def test_artikel01_has_correct_authors_list(testserver, testbrowser):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert article_view.authors_list == 'Anne Mustermann'


def test_artikel08_has_correct_authors_list(testserver, testbrowser):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/08')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert article_view.authors_list == 'Anne Mustermann;Oliver Fritsch'


def test_artikel05_has_set_text_length(testserver, testbrowser):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/05')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert article_view.text_length is not None


def test_article05_has_correct_dates(testserver, testbrowser):
    # updated article
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/05')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert article_view.date_last_published_semantic.isoformat() == (
        '2013-11-03T08:10:00.626737+01:00')
    assert article_view.date_first_released.isoformat() == (
        '2013-10-24T08:00:00+02:00')
    assert article_view.date_last_modified.isoformat() == (
        '2013-11-03T08:10:00.626737+01:00')


def test_article03_has_correct_dates(application):
    # not updated article
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert article_view.date_first_released.isoformat() == (
        '2013-07-30T17:20:50.176115+02:00')
    assert article_view.date_last_modified.isoformat() == (
        '2013-07-30T17:20:50.176115+02:00')


def test_article09_has_correct_date_formats(testserver, testbrowser):
    # print article, updated
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/09')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert article_view.show_date_format == 'long'
    assert article_view.show_date_format_seo == 'short'


def test_article10_has_correct_date_formats(testserver, testbrowser):
    # online article, updated
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/10')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert article_view.show_date_format == 'long'
    assert article_view.show_date_format_seo == 'long'


def test_article08_has_first_author(testserver, testbrowser):
    xml = 'http://xml.zeit.de/artikel/08'
    context = zeit.cms.interfaces.ICMSContent(xml)
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert article_view.authors[0]['name'] == u'Anne Mustermann'
    assert article_view.authors[0]['suffix'] == ' und'
    assert article_view.authors[0]['prefix'] == ' von'
    assert article_view.authors[0]['location'] == ', Berlin'


def test_article08_has_second_author(testserver, testbrowser):
    xml = 'http://xml.zeit.de/artikel/08'
    context = zeit.cms.interfaces.ICMSContent(xml)
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert article_view.authors[1]['name'] == u'Oliver Fritsch'
    assert article_view.authors[1]['suffix'] == ''
    assert article_view.authors[1]['prefix'] == ''
    assert article_view.authors[1]['location'] == ', London'


def test_article08_has_correct_genre(testserver, testbrowser):
    # 'ein'
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/08')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert article_view.genre == 'ein Kommentar'


def test_article09_has_correct_genre(testserver, testbrowser):
    # 'eine'
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/09')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert article_view.genre == 'eine Glosse'


def test_article05_has_no_genre(testserver, testbrowser):
    # no genre
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/05')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert article_view.genre is None


def test_article08_has_correct_source_label(testserver, testbrowser):
    # print source
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/08')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert article_view.source_label == u'DIE ZEIT Nr. 26/2008'


def test_article10_has_correct_source_label(testserver, testbrowser):
    # online source
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/10')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert article_view.source_label == 'Erschienen bei golem.de'


def test_article03_has_empty_source_label(application):
    # zon source
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert article_view.source_label is None


def test_article_has_correct_twitter_card_type(testserver, testbrowser):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert article_view.twitter_card_type == 'summary_large_image'


def test_longform_has_correct_twitter_card_type(testserver, testbrowser):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/05')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert article_view.twitter_card_type == 'summary_large_image'


def test_article_has_correct_sharing_image(testserver, testbrowser):
    xpath = testbrowser('/artikel/01').document.xpath
    source = testserver.url + '/exampleimages/artikel/01/schoppenstube/'\
        'wide__1300x731'
    assert xpath('//link[@itemprop="image"]/@href')[0] == source
    assert xpath('//meta[@property="og:image"]/@content')[0] == source
    assert xpath('//meta[@name="twitter:image"]/@content')[0] == source


def test_article_has_correct_product_id(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert article_view.product_id == 'ZEI'
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/10')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert article_view.product_id == 'GOLEM'


def test_article_page_should_throw_404_if_no_pages_are_exceeded(application):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    page = zeit.web.magazin.view_article.ArticlePage(article, mock.Mock())
    page.request.registry.settings = {}
    page.request.path_info = u'article/03/seite-9'
    with pytest.raises(pyramid.httpexceptions.HTTPNotFound):
        page()


def test_article_page_should_work_if_pages_from_request_fit(application):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    page = zeit.web.magazin.view_article.ArticlePage(
        article, pyramid.testing.DummyRequest())
    page.request.registry.settings = {}
    page.request.path_info = 'article/03/seite-3'
    page()
    assert len(page.pages) == 7


def test_article_page_komplett_should_show_all_pages(testserver, testbrowser):
    browser = testbrowser(
        '%s/artikel/03/komplettansicht' % testserver.url)
    assert 'Chianti ein Comeback wirklich verdient' in browser.contents


def test_pagination_dict_should_have_correct_entries(application):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    view = zeit.web.magazin.view_article.ArticlePage(article, mock.Mock())
    view.request.path_info = u'article/03/seite-2'
    view.request.traversed = (u'artikel', u'03')
    view.request.route_url.return_value = '/'

    assert view.pagination['current'] == 2
    assert view.pagination['total'] == 7
    assert view.pagination['next_page_title'] == (
        u'Sogar die eckige Flasche kommt zur\xfcck')

    view = zeit.web.magazin.view_article.Article(article, mock.Mock())
    view.request.traversed = ('artikel', '03')
    view.request.route_url.return_value = '/'

    assert view.pagination['current'] == 1
    assert view.pagination['total'] == 7
    assert view.pagination['next_page_title'] == (
        u'Sogar die runde Flasche kommt zur\xfcck')


def test_pagination_next_title_should_be_in_html(testserver, testbrowser):
    browser = testbrowser('%s/artikel/03/seite-2' % testserver.url)

    assert 'Auf Seite 3' in browser.contents
    assert 'Sogar die eckige Flasche kommt' in browser.contents


def test_pagination_urls_list_should_have_correct_entries_paged_article(
        application):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    view = zeit.web.magazin.view_article.ArticlePage(article, mock.Mock())
    view.request.path_info = u'article/03/seite-2'
    view.request.traversed = ('artikel', '03')
    view.request.route_url.return_value = '/'

    assert view.pages_urls[0] == '/artikel/03'
    assert view.pages_urls[1] == '/artikel/03/seite-2'
    assert view.pages_urls[2] == '/artikel/03/seite-3'


def test_pagination_urls_list_should_have_correct_entries_single_article(
        application):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    view = zeit.web.magazin.view_article.ArticlePage(article, mock.Mock())
    view.request.path_info = u'article/01'
    view.request.traversed = (u'artikel', u'01')
    view.request.route_url.return_value = '/'

    assert view.pages_urls[0] == '/artikel/01'
    assert len(view.pages_urls) == 1


def test_pagination_next_page_url_is_working(application):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    view = zeit.web.magazin.view_article.Article(article, mock.Mock())
    view.request.traversed = (u'artikel', u'03')
    view.request.route_url.return_value = '/'

    assert view.pagination['next_page_url'] == '/artikel/03/seite-2'


def test_pagination_next_page_url_on_last_page_is_none(application):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    view = zeit.web.magazin.view_article.ArticlePage(article, mock.Mock())
    view.request.path_info = u'article/03/seite-7'
    view.request.traversed = (u'artikel', u'03')
    view.request.route_url.return_value = '/'

    assert view.pagination['next_page_url'] is None


def test_pagination_prev_page_url_is_working(application):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    view = zeit.web.magazin.view_article.ArticlePage(article, mock.Mock())
    view.request.path_info = u'article/03/seite-2'
    view.request.traversed = (u'artikel', u'03')
    view.request.route_url.return_value = '/'

    assert view.pagination['prev_page_url'] == u'/artikel/03'


def test_pagination_prev_page_url_on_first_page_is_none(application):
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/03')
    view = zeit.web.magazin.view_article.Article(article, mock.Mock())
    view.request.traversed = ('artikel', '03')
    view.request.route_url.return_value = '/'
    assert view.pagination['prev_page_url'] is None


def test_article09_should_have_a_nextread(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/09')
    view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert len(view.nextread) == 1
    assert view.nextread[0] is not None


def test_article01_should_not_have_nextread_teasers(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert len(view.nextread) == 0


def test_caching_headers_should_be_set(testserver, testbrowser):
    browser = testbrowser('%s/artikel/05' % testserver.url)
    assert browser.headers['cache-control'] == 'max-age=10'


def test_article_should_have_correct_js_view(testbrowser, testserver):
    bc = testbrowser('%s/artikel/01' % testserver.url).contents
    assert "window.Zeit = {" in bc
    assert "'banner_channel': 'zeitmz/modeunddesign/article'," in bc
    assert "'ressort': 'zeit-magazin'," in bc
    assert "'sub_ressort': 'mode-design'," in bc
    assert "'type': 'article'," in bc


def test_centerpage_should_have_correct_js_view(testserver, testbrowser):
    bc = testbrowser(
        '%s/centerpage/lebensart' % testserver.url).contents
    assert "window.Zeit = {" in bc
    assert "'banner_channel': 'zeitmz/leben/centerpage'," in bc
    assert "'ressort': 'lebensart'," in bc
    assert "'sub_ressort': 'leben'," in bc
    assert "'type': 'centerpage'," in bc


def test_gallery_should_have_correct_js_view(testserver, testbrowser):
    b = testbrowser(
        '%s/galerien/fs-desktop-schreibtisch-computer' % testserver.url)
    bc = b.contents
    assert "window.Zeit = {" in bc
    assert "'banner_channel': 'zeitmz/leben/article'," in bc
    assert "'sub_ressort': 'leben'," in bc
    assert "'ressort': 'zeit-magazin'," in bc
    assert "'type': 'gallery'," in bc


def test_iqd_mobile_settings_are_filled(application):
    # tested just as examlpe for an article here, all possible combinations
    # are tested in test_banner.py integration tests
    article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    view = zeit.web.magazin.view_article.Article(
        article, mock.MagicMock(return_value=''))
    assert view.iqd_mobile_settings.get('top') == '445612'
    assert view.iqd_mobile_settings.get('middle') == '445612'
    assert view.iqd_mobile_settings.get('bottom') == '445612'


def test_http_header_should_contain_version(testserver, testbrowser):
    pkg = pkg_resources.get_distribution('zeit.web')
    pkg_version = pkg.version
    head_version = requests.head(
        testserver.url + "/zeit-magazin/index").headers['x-version']
    assert pkg_version == head_version


def test_feature_longform_template_should_have_zon_logo_header(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/feature_longform.html')

    # jinja2 has a blocks attribute which generates a stream,
    # if called with context. We can use it with a html parser.
    ctx, request = (mock.Mock(),) * 2
    # It seems jinja evaluates {{request.route_url('home')}} not like
    # getattr(ctx.resolve('request'), 'route_url')('home'), but more like
    # ctx.call('request.route_url', 'home')
    ctx.call.return_value = 'http://foo.bar/'

    html_str = ' '.join(list(tpl.blocks['longform_logo'](ctx)))
    html = lxml.html.fromstring(html_str)
    elem = html.cssselect('.main-nav__logo__img.icon-logo-zon-large')[0]
    assert elem.text == 'ZEIT ONLINE'
    assert elem.get('title') == 'ZEIT ONLINE'

    elem = html.cssselect('.main-nav__logo')[0]
    assert elem.get('href') == 'http://foo.bar/index'


def test_feature_longform_template_should_have_zon_logo_footer(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/feature_longform.html')
    html_str = " ".join(list(tpl.blocks['footer_logo']({})))
    html = lxml.html.fromstring(html_str)
    assert len(html.cssselect('.main-footer__logo.icon-logo-zon-small')) == 1


def test_advertorial_is_advertorial(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/centerpage/advertorial')
    assert zeit.web.core.view.is_advertorial(context, mock.Mock())

    view = zeit.web.magazin.view_centerpage.Centerpage(context, mock.Mock())
    assert view.type == 'centerpage'

    cp_context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/centerpage/index')
    assert not zeit.web.core.view.is_advertorial(cp_context, mock.Mock())


def test_adv_teaser_on_cp_should_render_modifier(testserver, testbrowser):
    browser = testbrowser('%s/centerpage/index' % testserver.url)
    assert browser.cssselect('.is-advertorial')


def test_adv_teaser_on_adv_should_not_render_modifier(testserver, testbrowser):
    browser = testbrowser('%s/centerpage/advertorial' % testserver.url)
    assert not browser.cssselect('.is-advertorial')


def test_ressort_literally_returns_correct_ressort(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/index')
    view = zeit.web.magazin.view_centerpage.Centerpage(context, mock.Mock())
    assert view.ressort_literally == 'ZEITmagazin'
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/artikel/02')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert article_view.ressort_literally == 'ZEITmagazin'
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/artikel/01')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert article_view.ressort_literally == 'Mode & Design'
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/leben/2014-05/'
        'Martenstein-Online-Kommentare')
    article_view = zeit.web.magazin.view_article.Article(context, mock.Mock())
    assert article_view.ressort_literally == 'Leben'
