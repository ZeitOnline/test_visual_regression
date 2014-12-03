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


def test_buzz_mostread_should_render_correct_article_count(
        testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/main-teaser-setup' % testserver.url)
    assert len(browser.cssselect('.teaser--buzz-mostread')) == 3


def test_buzz_mostread_should_render_with_correct_scores(
        testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/main-teaser-setup' % testserver.url)
    media = browser.cssselect('.numeric--buzz-mostread')
    assert [int(m.text.strip('\n    ')) for m in media] == [1, 2, 3]


def test_buzz_mostread_should_output_correct_titles(
        testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/main-teaser-setup' % testserver.url)
    kicker = browser.cssselect('.teaser__heading--buzz-mostread '
                               '.teaser__combined-link .teaser__kicker')[0]
    assert 'Gentrifizierung' in kicker.text
    title = browser.cssselect('.teaser__heading--buzz-mostread '
                              '.teaser__combined-link .teaser__title')[1]
    assert 'Den Tod tragen unter der Sonne' in title.text


def test_buzz_comments_should_render_correct_article_count(
        testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/main-teaser-setup' % testserver.url)
    assert len(browser.cssselect('.teaser--buzz-comments')) == 3


def test_buzz_comments_should_render_with_correct_scores(
        testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/main-teaser-setup' % testserver.url)
    media = browser.cssselect('.numeric--buzz-comments')
    assert [int(m.text.strip('\n    ')) for m in media] == [129, 142, 110]


def test_buzz_comments_should_output_correct_titles(
        testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/main-teaser-setup' % testserver.url)
    kicker = browser.cssselect('.teaser__heading--buzz-comments '
                               '.teaser__combined-link .teaser__kicker')[0]
    assert 'Gentrifizierung' in kicker.text
    title = browser.cssselect('.teaser__heading--buzz-comments '
                              '.teaser__combined-link .teaser__title')[1]
    assert 'Den Tod tragen unter der Sonne' in title.text


def test_buzz_facebook_should_render_correct_article_count(
        testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/main-teaser-setup' % testserver.url)
    assert len(browser.cssselect('.teaser--buzz-facebook')) == 3


def test_buzz_facebook_should_render_with_correct_scores(
        testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/main-teaser-setup' % testserver.url)
    media = browser.cssselect('.annotated-icon--buzz-facebook '
                              '.annotated-icon__label')
    assert [int(m.text.strip('\n    ')) for m in media] == [16674, 5780, 2391]


def test_buzz_facebook_should_output_correct_titles(
        testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/main-teaser-setup' % testserver.url)
    kicker = browser.cssselect('.teaser__heading--buzz-facebook '
                               '.teaser__combined-link .teaser__kicker')[0]
    assert 'Spitzmarke' in kicker.text
    title = browser.cssselect('.teaser__heading--buzz-facebook '
                              '.teaser__combined-link .teaser__title')[1]
    assert 'Pegah Ferydoni' in title.text


def test_tile7_is_rendered_on_correct_position(
        testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/main-teaser-setup' % testserver.url)
    html = browser.cssselect
    assert html('.main__informatives div')[0].attrib['class'] != \
        'ad__tile_7 ad__on__centerpage ad__width_300 ad__min__768', (
            'there should be no iqadtile7')
    assert html('.main__informatives div')[6].attrib['id'] == \
        'iqadtile7', ('iqadtile7 not present')


def test_tile7_for_fullwidth_is_rendered_on_correct_position(
        testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/index' % testserver.url)
    html = browser.cssselect
    assert html('.main__informatives div')[0].attrib['id'] == 'iqadtile7', (
        'iqadtile7 not present')
