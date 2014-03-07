from urllib2 import HTTPError
from zeit.content.article.edit.reference import Gallery
from zeit.frontend import view
from zeit.frontend import view_article
from zeit.frontend.block import InlineGalleryImage
from zope.testbrowser.browser import Browser
import mock
import pytest
import requests
import zeit.cms.interfaces


def test_breadcumb_should_produce_expected_data():
    context = mock.Mock()
    context.ressort = 'mode'
    context.sub_ressort = 'lebensart'
    context.title = 'This is my title'

    view_article._navigation = {
        'start': ('Start', 'http://www.zeit.de/index', 'myid1'),
        'zmo': ('ZEIT Magazin', 'http://www.zeit.de/magazin/index', 'myid2'),
        'lebensart': ('lebensart',
                      'http://www.zeit.de/magazin/lebensart/index',
                      'myid3'),
        'mode': ('mode', 'http://www.zeit.de/magazin/mode/index', 'myid4'), }

    article = view_article.Article(context, '')

    l = [
        ('Start', 'http://www.zeit.de/index', 'myid1'),
        ('ZEIT Magazin', 'http://www.zeit.de/magazin/index', 'myid2'),
        ('mode', 'http://www.zeit.de/magazin/mode/index', 'myid4'),
        ('lebensart', 'http://www.zeit.de/magazin/lebensart/index',
            'myid3'),
        ('This is my title', 'http://localhost'), ]

    assert article.breadcrumb == l


def test_breadcrumb_should_be_shorter_if_ressort_or_sub_ressort_is_unknown():
    context = mock.Mock()
    context.ressort = 'modex'
    context.sub_ressort = 'lebensartx'
    context.title = 'This is my title'

    view_article._navigation = {
        'start': ('Start', 'http://www.zeit.de/index', 'myid1'),
        'zmo': ('ZEIT Magazin', 'http://www.zeit.de/magazin/index', 'myid2'),
        'lebensart': ('lebensart',
                      'http://www.zeit.de/magazin/lebensart/index',
                      'myid3'),
        'mode': ('mode', 'http://www.zeit.de/magazin/mode/index', 'myid4'), }

    article = view_article.Article(context, '')

    l = [
        ('Start', 'http://www.zeit.de/index', 'myid1'),
        ('ZEIT Magazin', 'http://www.zeit.de/magazin/index',
            'myid2'),
        ('This is my title', 'http://localhost'), ]

    assert article.breadcrumb == l


def test_header_img_should_be_first_image_of_content_blocks(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/05')
    article_view = view_article.Article(context, '')
    url = 'http://xml.zeit.de/exampleimages/artikel/05/01.jpg'
    assert article_view.header_img.src == url


def test_header_img_should_be_none_if_we_have_a_wrong_layout(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    article_view = view_article.Article(context, '')
    assert article_view.header_img is None


def test_header_video_should_be_first_video_of_content_blocks(application):
    vid_url = 'http://xml.zeit.de/artikel/header_video'
    context = zeit.cms.interfaces.ICMSContent(vid_url)
    article_view = view_article.Article(context, '')
    url = 'http://brightcove.vo.llnwd.net/pd15/media/18140073001/201401/' \
        '3809/18140073001_3094832002001_Aurora-Borealis--Northern-Lights' \
        '--Time-lapses-in-Norway-Polarlichter-Der-Himmel-brennt.mp4'
    assert article_view.header_video.source == url


def test_header_video_should_be_none_if_we_have_a_wrong_layout(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    article_view = view_article.Article(context, '')
    assert article_view.header_video is None


def test_header_elem_should_be_img_if_there_is_a_header_img(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/05')
    article_view = view_article.Article(context, '')
    assert type(article_view.header_elem) == zeit.frontend.block.HeaderImage


def test_header_elem_should_be_video_if_there_is_a_header_video(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/header_video')
    article_view = view_article.Article(context, '')
    assert type(article_view.header_elem) == zeit.frontend.block.HeaderVideo


def test_header_image_should_be_none_if_adapted_as_regular_image(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/05')
    body = zeit.content.article.edit.interfaces.IEditableBody(context)
    assert zeit.frontend.block.Image(body.values()[0]) is None


def test_image_view_returns_image_data_for_filesystem_connector(testserver):
    r = requests.get(testserver.url + '/exampleimages/artikel/01/01.jpg')
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
    assert type(frontend_gallery.items()[3]) == InlineGalleryImage

    gallery_image = frontend_gallery.items()[3]
    assert gallery_image.src == u'http://xml.zeit.de/galerien/bg-automesse-detroit-2014-usa-bilder/chrysler 200 s 1-540x304.jpg'
    assert gallery_image.alt == None
    assert gallery_image.copyright == u'\xa9'


def test_article_request_should_have_body_element(testserver):
    browser = Browser('%s/artikel/05' % testserver.url)
    assert '<body itemscope itemtype="http://schema.org/WebPage">' in browser.contents
    assert '</body>' in browser.contents


def test_article_request_should_have_html5_doctype(testserver):
    browser = Browser('%s/artikel/05' % testserver.url)
    assert '<!DOCTYPE html>' in browser.contents


def test_artikel05_should_have_header_image(testserver):
    browser = Browser('%s/artikel/05' % testserver.url)
    assert '<div class="article__head-wrap">' in browser.contents
    assert '<div class="scaled-image is-pixelperfect">' in browser.contents
    assert '<img class="article__main-image--longform"' in browser.contents

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
    article_view = view_article.Article(context, '')
    assert article_view.tracking_type == 'Artikel'


def test_artikel02_has_lebensart_ressort(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/02')
    article_view = view_article.Article(context, '')
    assert article_view.ressort == 'lebensart'


def test_artikel02_has_mode_sub_ressort(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/02')
    article_view = view_article.Article(context, '')
    assert article_view.sub_ressort == 'mode'


def test_artikel02_has_correct_banner_channel(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/02')
    article_view = view_article.Article(context, '')
    assert article_view.banner_channel == 'lebensart/mode/article'


def test_artikel05_has_rankedTagsList(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/05')
    article_view = view_article.Article(context, '')
    assert article_view.rankedTagsList is not None
    assert article_view.rankedTagsList != ''


def test_artikel05_has_set_text_length(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/05')
    article_view = view_article.Article(context, '')
    assert article_view.text_length is not None


def test_article05_has_date_formats(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/05')
    article_view = view_article.Article(context, '')
    assert article_view.date_last_published_semantic is not None
    assert article_view.date_first_released is not None
    assert article_view.show_article_date is not None


def test_article01__has_correct_twitter_card_type(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    article_view = view_article.Article(context, '')
    assert article_view.twitter_card_type == 'summary'


def test_article05_has_correct_twitter_card_type(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/05')
    article_view = view_article.Article(context, '')
    assert article_view.twitter_card_type == 'summary_large_image'


def test_article01_has_correct_sharing_img_src(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    article_view = view_article.Article(context, '')
    assert article_view.sharing_img.src == \
        'http://xml.zeit.de/exampleimages/artikel/01/01.jpg'


def test_article06_has_correct_sharing_img_video_still(testserver):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/06')
    article_view = view_article.Article(context, '')
    assert article_view.sharing_img.video_still == \
        'http://brightcove.vo.llnwd.net/d21/unsecured/media/18140073001/' \
        '201401/3097/18140073001_3094729885001_7x.jpg'
