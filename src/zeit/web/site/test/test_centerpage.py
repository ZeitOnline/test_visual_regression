import datetime

import mock

import zeit.cms.interfaces

import zeit.web.site.view_centerpage


def test_centerpage_has_last_semantic_change_property(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/centerpage/zeitonline')
    view = zeit.web.site.view_centerpage.Centerpage(context, mock.Mock())

    assert isinstance(view.last_semantic_change, datetime.datetime)
    assert view.last_semantic_change.strftime('%d %b %y') == '21 May 14'


def test_buzz_mostread_should_render_with_correct_scores(
        testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/main-teaser-setup' % testserver.url)
    assert len(browser.cssselect('.teaser--buzz-mostread')) == 3
    media = browser.cssselect('.numeric--buzz-mostread')
    assert [int(m.text.strip('\n    ')) for m in media] == [1, 2, 3]


def test_buzz_facebook_should_render_with_correct_scores(
        testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/main-teaser-setup' % testserver.url)
    assert len(browser.cssselect('.teaser--buzz-facebook')) == 3
    media = browser.cssselect('.annotated-icon--buzz-facebook .label')
    assert [int(m.text.strip('\n    ')) for m in media] == [16674, 5780, 2391]
