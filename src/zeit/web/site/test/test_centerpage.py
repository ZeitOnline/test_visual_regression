# -*- coding: utf-8 -*-

import datetime
import re

import mock

import zeit.cms.interfaces

import zeit.web.site.view_centerpage


def to_int(value, pattern=re.compile(r'[^\d.]+')):
    return int(pattern.sub('', value))


def test_centerpage_has_last_semantic_change_property(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/centerpage/zeitonline')
    view = zeit.web.site.view_centerpage.Centerpage(context, mock.Mock())

    assert isinstance(view.last_semantic_change, datetime.datetime)
    assert view.last_semantic_change.strftime('%d %b %y') == '21 May 14'


def test_buzz_mostread_should_render_correct_article_count(
        testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/main-teaser-setup' % testserver.url)
    articles = browser.cssselect('.buzz-box__teasers--buzz-mostread article')
    assert len(articles) == 3


def test_buzz_mostread_should_render_with_correct_indices(
        testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/main-teaser-setup' % testserver.url)
    media = browser.cssselect('.buzz-index__label--buzz-mostread')
    assert [to_int(m.text) for m in media] == [1, 2, 3]


def test_buzz_mostread_should_output_correct_titles(
        testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/main-teaser-setup' % testserver.url)
    kicker = browser.cssselect('.buzz-mostread__kicker')[0]
    assert u'Gentrifizierung' in kicker.text
    title = browser.cssselect('.buzz-mostread__title')[1]
    assert u'Das neue Heft \x96 im Video durchgeblättert' in title.text


def test_buzz_comments_should_render_correct_article_count(
        testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/main-teaser-setup' % testserver.url)
    articles = browser.cssselect('.buzz-box__teasers--buzz-comments article')
    assert len(articles) == 3


def test_buzz_comments_should_render_with_correct_scores(
        testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/main-teaser-setup' % testserver.url)
    media = browser.cssselect('.buzz-line__label--buzz-comments')
    assert [to_int(m.text) for m in media] == [129, 142, 110]


def test_buzz_comments_should_output_correct_titles(
        testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/main-teaser-setup' % testserver.url)
    kicker = browser.cssselect('.buzz-comments__kicker')[0]
    assert u'Gentrifizierung' in kicker.text
    title = browser.cssselect('.buzz-comments__title')[1]
    assert u'Das neue Heft \x96 im Video durchgeblättert' in title.text


def test_buzz_facebook_should_render_correct_article_count(
        testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/main-teaser-setup' % testserver.url)
    articles = browser.cssselect('.buzz-box__teasers--buzz-facebook article')
    assert len(articles) == 3


def test_buzz_facebook_should_render_with_correct_scores(
        testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/main-teaser-setup' % testserver.url)
    media = browser.cssselect('.buzz-line__label--buzz-facebook')
    assert [to_int(m.text) for m in media] == [16674, 5780, 2391]


def test_buzz_facebook_should_output_correct_titles(
        testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/main-teaser-setup' % testserver.url)
    kicker = browser.cssselect('.buzz-facebook__kicker')[0]
    assert u'Jens Spahn' in kicker.text
    title = browser.cssselect('.buzz-facebook__title')[1]
    assert u'Shakespeare im Kugelhagel' in title.text


def test_tile7_is_rendered_on_correct_position(
        testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/main-teaser-setup' % testserver.url)
    informatives = browser.cssselect('.main__informatives div')
    assert informatives[0].attrib['class'] != (
        'ad__tile_7 ad__on__centerpage ad__width_300 ad__min__768'), (
        'There should be no iqadtile7.')
    assert informatives[9].attrib['id'] == 'iqadtile7', (
        'Tile iqadtile7 is not present.')


def test_tile7_for_fullwidth_is_rendered_on_correct_position(
        testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/index' % testserver.url)
    informatives = browser.cssselect('.main__informatives div')
    assert informatives[0].attrib['id'] == 'iqadtile7', (
        'Tile iqadtile7 is not present.')
