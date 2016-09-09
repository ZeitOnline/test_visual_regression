# -*- coding: utf-8 -*-

import zeit.cms.interfaces
import zeit.web.magazin.view_article


def test_comments_template_respects_metadata(tplbrowser, dummy_request):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/01')
    dummy_request.user = {'ssoid': 123, 'uid': '123', 'name': 'Max'}
    view = zeit.web.magazin.view_article.Article(content, dummy_request)
    view.commenting_allowed = False
    comments = tplbrowser('zeit.web.core:templates/inc/article/comments.html',
                          view=view, request=dummy_request)
    assert len(comments.cssselect('.comment-section')) == 1, (
        'comment section must be present')

    thread = tplbrowser('zeit.web.core:templates/inc/comments/thread.html',
                        view=view, request=dummy_request)
    assert len(thread.cssselect('article.comment')) > 0, (
        'comments must be displayed')

    form = tplbrowser('zeit.web.core:templates/inc/comments/comment-form.html',
                      view=view, request=dummy_request)
    assert len(form.cssselect('#comment-form[data-uid="123"]')) == 1, (
        'comment form tag with data-uid attribute must be present')
    assert len(form.cssselect('#comment-form textarea')) == 0, (
        'comment form must be empty')

    view.show_commentthread = False
    comments = tplbrowser('zeit.web.core:templates/inc/article/comments.html',
                          view=view, request=dummy_request)
    assert comments.xpath('//body/*') == [], (
        'comment section template must return an empty document')


def test_comments_and_replies_do_appear(testserver, httpbrowser):
    browser = httpbrowser('%s/zeit-magazin/article/01' % testserver.url)
    comments = browser.cssselect('article.comment')
    assert 'Jetzt aber los.' in comments[0].text_content().strip()
    assert 'comment--indented' in comments[1].get('class')
    assert 'ja, echt?' in comments[1].text_content().strip()
