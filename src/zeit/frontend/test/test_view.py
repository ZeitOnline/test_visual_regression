import mock
import zeit.cms.interfaces
from zeit.frontend import view
import mock
import requests


def test_breadcumb_should_produce_expected_data():
    context = mock.Mock()
    context.ressort = 'mode'
    context.sub_ressort = 'lebensart'
    context.title = 'This is my title'

    view._navigation = {
        'start': ('Start', 'http://www.zeit.de/index', 'myid1'),
        'zmo': ('ZEIT Magazin', 'http://www.zeit.de/magazin/index', 'myid2'),
        'lebensart': ('lebensart',
                      'http://www.zeit.de/magazin/lebensart/index',
                      'myid3'),
        'mode': ('mode', 'http://www.zeit.de/magazin/mode/index', 'myid4'), }

    article = view.Article(context, '')

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

    view._navigation = {
        'start': ('Start', 'http://www.zeit.de/index', 'myid1'),
        'zmo': ('ZEIT Magazin', 'http://www.zeit.de/magazin/index', 'myid2'),
        'lebensart': ('lebensart',
                      'http://www.zeit.de/magazin/lebensart/index',
                      'myid3'),
        'mode': ('mode', 'http://www.zeit.de/magazin/mode/index', 'myid4'), }

    article = view.Article(context, '')

    l = [
        ('Start', 'http://www.zeit.de/index', 'myid1'),
        ('ZEIT Magazin', 'http://www.zeit.de/magazin/index',
            'myid2'),
        ('This is my title', 'http://localhost'), ]

    assert article.breadcrumb == l


def test_header_img_should_be_first_image_of_content_blocks(application):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    article_view = view.Article(context, '')
    url = 'http://xml.zeit.de/exampleimages/artikel/01/01.jpg'
    assert article_view.header_img.src == url

    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/05')
    article_view = view.Article(context, '')
    url = 'http://xml.zeit.de/exampleimages/artikel/05/01.jpg'
    assert article_view.header_img.src == url


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
    article_view = view.Article(context, '')
    body = zeit.content.article.edit.interfaces.IEditableBody(context)
    assert body.values == []
