import lxml.etree
import mock
import zope.component

from zeit.cms.checkout.helper import checked_out
import zeit.cms.interfaces
import zeit.content.article.article
import zeit.content.article.edit.interfaces
import zeit.retresco.connection

import zeit.web.core.article
import zeit.web.core.interfaces


def test_video_should_be_removed_from_body_if_layout_is_header(application):
    article = zeit.content.article.article.Article()
    block = article.body.create_item('video')
    block.video = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/video/3537342483001')

    pages = zeit.web.core.article.pages_of_article(article)
    assert len(pages[0]) == 1

    block.layout = u'zmo-xl-header'
    pages = zeit.web.core.article.pages_of_article(article)
    assert len(pages[0]) == 0


def test_retresco_body_should_respect_toggle_off(application, monkeypatch):
    assert zeit.web.core.application.FEATURE_TOGGLES.find(
        'enable_intext_links') is False

    get_article_body = mock.Mock(return_value='')
    monkeypatch.setattr(
        zeit.retresco.connection.TMS, 'get_article_body', get_article_body)

    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    zeit.content.article.edit.interfaces.IEditableBody(article)

    assert get_article_body.call_count == 0


def test_retresco_body_should_respect_seo_flag(application, monkeypatch):
    zeit.web.core.application.FEATURE_TOGGLES.set('enable_intext_links')

    get_article_body = mock.Mock(return_value='')
    monkeypatch.setattr(
        zeit.retresco.connection.TMS, 'get_article_body', get_article_body)

    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/intext-disabled')
    zeit.content.article.edit.interfaces.IEditableBody(article)

    assert get_article_body.call_count == 0


def test_retresco_body_should_replace_xml_body(application, monkeypatch):
    zeit.web.core.application.FEATURE_TOGGLES.set('enable_intext_links')

    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    conf['retresco_timeout'] = 0.42

    get_article_body = mock.Mock(
        return_value='<body><a href="http://foo">topicpage</a></body>')
    monkeypatch.setattr(
        zeit.retresco.connection.TMS, 'get_article_body', get_article_body)

    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    body = zeit.content.article.edit.interfaces.IEditableBody(article)

    assert get_article_body.call_args == [(article,), {'timeout': 0.42}]
    assert body.xml.find('a') == 'topicpage'


def test_retresco_body_xml_should_be_cached(application, monkeypatch):
    zeit.web.core.application.FEATURE_TOGGLES.set('enable_intext_links')
    get_article_body = mock.Mock(
        return_value='<body><a href="http://foo">topicpage</a></body>')
    monkeypatch.setattr(
        zeit.retresco.connection.TMS, 'get_article_body', get_article_body)
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    b1 = zeit.content.article.edit.interfaces.IEditableBody(article)
    assert get_article_body.call_count == 1
    b2 = zeit.content.article.edit.interfaces.IEditableBody(article)
    assert get_article_body.call_count == 1
    assert lxml.etree.tostring(b1.xml) == lxml.etree.tostring(b2.xml)


def test_skips_blocks_with_errors(application):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/portraitbox_invalid')
    with mock.patch('zeit.web.core.block.Portraitbox.__init__') as pbox:
        pbox.side_effect = RuntimeError('provoked')
        pages = zeit.web.core.article.pages_of_article(article)
    assert len(pages) == 1


def test_editable_body_should_calculate_values_only_once(application):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    m1 = article.body.values()[0]
    m2 = article.body.values()[0]
    assert m1 is m2
