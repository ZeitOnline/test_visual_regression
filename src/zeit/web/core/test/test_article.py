import zeit.cms.interfaces
import zeit.content.article.article
import zeit.content.article.edit.interfaces


def test_video_should_be_removed_from_body_if_layout_is_header(application):
    article = zeit.content.article.article.Article()
    body = zeit.content.article.edit.interfaces.IEditableBody(article)
    block = body.create_item('video')
    block.video = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/video/3537342483001')

    pages = zeit.web.core.interfaces.IPages(article)
    assert len(pages[0]) == 1

    block.layout = u'zmo-xl-header'
    pages = zeit.web.core.interfaces.IPages(article)
    assert len(pages[0]) == 0
