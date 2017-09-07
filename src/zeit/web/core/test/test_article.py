import mock
import zope.component

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
    zope.component.getAdapter(
        article,
        zeit.content.article.edit.interfaces.IEditableBody,
        name='retresco')

    assert get_article_body.call_count == 0


def test_retresco_body_should_respect_seo_flag(application, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'enable_intext_links': True}.get)

    get_article_body = mock.Mock(return_value='')
    monkeypatch.setattr(
        zeit.retresco.connection.TMS, 'get_article_body', get_article_body)

    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/intext-disabled')
    zope.component.getAdapter(
        article,
        zeit.content.article.edit.interfaces.IEditableBody,
        name='retresco')

    assert get_article_body.call_count == 0


def test_retresco_body_should_replace_xml_body(application, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'enable_intext_links': True}.get)

    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    conf['retresco_timeout'] = 0.42

    get_article_body = mock.Mock(
        return_value='<body><a href="http://foo">topicpage</a></body>')
    monkeypatch.setattr(
        zeit.retresco.connection.TMS, 'get_article_body', get_article_body)

    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    body = zope.component.getAdapter(
        article,
        zeit.content.article.edit.interfaces.IEditableBody,
        name='retresco')

    assert get_article_body.call_args == [
        ('{urn:uuid:9e7bf051-2299-43e4-b5e6-1fa81d097dbd}',),
        {'timeout': 0.42}]
    assert body.xml.find('a') == 'topicpage'


def test_skips_blocks_with_errors(application):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/portraitbox_invalid')
    with mock.patch('zeit.web.core.block.Portraitbox.__init__') as pbox:
        pbox.side_effect = RuntimeError('provoked')
        pages = zeit.web.core.article.pages_of_article(article)
    assert len(pages) == 1
