# -*- coding: utf-8 -*-

import datetime

import lxml.html
import mock
import pysolr
import pytest

import zeit.cms.interfaces
from zeit.cms.checkout.helper import checked_out

from zeit.web.core.utils import to_int
import zeit.web.site.view_centerpage


def test_centerpage_has_last_semantic_change_property(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/centerpage/zeitonline')
    view = zeit.web.site.view_centerpage.Centerpage(context, mock.Mock())

    assert isinstance(view.last_semantic_change, datetime.datetime)
    assert view.last_semantic_change.strftime('%d %b %y') == '21 May 14'


def test_buzz_mostread_should_render_correct_article_count(testbrowser):
    browser = testbrowser('/zeit-online/buzz-box')
    box = browser.cssselect('.buzz-box--mostread')
    items = browser.cssselect('.buzz-box--mostread li')
    articles = browser.cssselect('.buzz-box--mostread article.teaser-buzz')
    assert len(box) == 1
    assert len(items) == 3
    assert len(articles) == 3


def test_buzz_mostread_should_output_correct_titles(testbrowser):
    browser = testbrowser('/zeit-online/buzz-box')
    kicker = browser.cssselect('.teaser-buzz__kicker')
    titles = browser.cssselect('.teaser-buzz__title')
    assert kicker and u'"Game of Thrones"' in kicker[0].text
    assert titles and u'Es gibt keinen Himmel über Westeros' in titles[0].text


@pytest.mark.skipif(True,
                    reason='Hidden until referrer-sensitive buzzbox is added.')
def test_buzz_comments_should_render_correct_article_count(
        testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/main-teaser-setup' % testserver.url)
    articles = browser.cssselect('.buzz-box__teasers--buzz-comments article')
    assert len(articles) == 3


@pytest.mark.skipif(True,
                    reason='Hidden until referrer-sensitive buzzbox is added.')
def test_buzz_comments_should_render_with_correct_scores(
        testbrowser, testserver, mockserver_factory):
    cp_counts = """<?xml version="1.0" encoding="UTF-8"?>
    <nodes>
        <node comment_count="129" url="/artikel/01"/>
        <node comment_count="142" url="/artikel/02"/>
        <node comment_count="110" url="/artikel/03"/>
    </nodes>
    """
    mockserver_factory(cp_counts)
    browser = testbrowser('%s/zeit-online/main-teaser-setup' % testserver.url)
    media = browser.cssselect('.buzz-line__label--buzz-comments')
    assert [to_int(m.text) for m in media] == [129, 142, 110]


@pytest.mark.skipif(True,
                    reason='Hidden until referrer-sensitive buzzbox is added.')
def test_buzz_comments_should_output_correct_titles(
        testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/main-teaser-setup' % testserver.url)
    kicker = browser.cssselect('.buzz-comments__kicker')[0]
    assert u'Gentrifizierung' in kicker.text
    title = browser.cssselect('.buzz-comments__title')[1]
    assert u'Das neue Heft \x96 im Video durchgeblättert' in title.text


@pytest.mark.skipif(True,
                    reason='Hidden until referrer-sensitive buzzbox is added.')
def test_buzz_facebook_should_render_correct_article_count(
        testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/main-teaser-setup' % testserver.url)
    articles = browser.cssselect('.buzz-box__teasers--buzz-facebook article')
    assert len(articles) == 3


@pytest.mark.skipif(True,
                    reason='Hidden until referrer-sensitive buzzbox is added.')
def test_buzz_facebook_should_render_with_correct_scores(
        testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/main-teaser-setup' % testserver.url)
    media = browser.cssselect('.buzz-line__label--buzz-facebook')
    assert [to_int(m.text) for m in media] == [16674, 5780, 2391]


@pytest.mark.skipif(True,
                    reason='Hidden until referrer-sensitive buzzbox is added.')
def test_buzz_facebook_should_output_correct_titles(
        testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/main-teaser-setup' % testserver.url)
    kicker = browser.cssselect('.buzz-facebook__kicker')[0]
    assert u'Jens Spahn' in kicker.text
    title = browser.cssselect('.buzz-facebook__title')[1]
    assert u'Shakespeare im Kugelhagel' in title.text


def test_tile7_is_rendered_on_correct_position(testbrowser):
    browser = testbrowser('/zeit-online/main-teaser-setup')
    tile7_on_first_position = browser.cssselect(
        '.cp-area--minor > div:first-child > script[id="ad-desktop-7"]')
    tile7_is_present = browser.cssselect(
        '.cp-area--minor > div > script[id="ad-desktop-7"]')

    assert not tile7_on_first_position, (
        'There should be no ad tile 7 on the first position.')
    assert tile7_is_present, (
        'Ad tile 7 is not present.')


def test_tile7_for_fullwidth_is_rendered_on_correct_position(testbrowser):
    browser = testbrowser('/zeit-online/index')
    tile7_on_first_position = browser.cssselect(
        '.cp-area--minor > div:first-child > script[id="ad-desktop-7"]')
    assert tile7_on_first_position, (
        'Ad tile 7 is not present on first position.')


def test_printbox_is_present_and_has_digital_offerings(
        testbrowser, testserver, workingcopy):
    uri = 'http://xml.zeit.de/angebote/print-box'
    content = zeit.cms.interfaces.ICMSContent(uri)
    with checked_out(content) as co:
        co.byline = 'mo-mi'
    browser = testbrowser('%s/zeit-online/index' % testserver.url)
    printbox = browser.cssselect('.print-box:not(.print-box--angebot)')
    anbebotsbox = browser.cssselect('.print-box--angebot')

    assert len(printbox) == 0
    assert len(anbebotsbox) == 1


def test_printbox_is_present_and_has_newsprint_offerings(
        testbrowser, testserver, workingcopy):
    uri = 'http://xml.zeit.de/angebote/print-box'
    content = zeit.cms.interfaces.ICMSContent(uri)
    with checked_out(content) as co:
        co.byline = ''
    browser = testbrowser('%s/zeit-online/index' % testserver.url)
    printbox = browser.cssselect('.print-box:not(.print-box--angebot)')
    anbebotsbox = browser.cssselect('.print-box--angebot')

    assert len(printbox) == 1
    assert len(anbebotsbox) == 0


def test_centerpage_should_gracefully_skip_all_broken_references(
        testbrowser, testserver):
    browser = testbrowser(
        '{}/zeit-online/teaser-broken-setup'.format(testserver.url))
    # @todo these class names are all gone
    assert not browser.cssselect('.main__fullwidth .teasers-fullwidth *')
    assert not browser.cssselect('.teaser-collection .teasers *')
    assert not browser.cssselect('.main__parquet .parquet *')
    assert not browser.cssselect('.main__snapshot *')


def test_dynamic_centerpage_collection_should_output_teasers(
        monkeypatch, application):
    def search(self, q, **kw):
        return pysolr.Results(
            [{'uniqueId': 'http://xml.zeit.de/artikel/0%s' % i}
                for i in range(1, 9)], 8)

    monkeypatch.setattr(zeit.web.core.sources.Solr, 'search', search)
    cp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/dynamic/ukraine')
    view = zeit.web.site.view_centerpage.Centerpage(cp, mock.Mock())
    counter = 0
    for region in view.regions:
            for area in region.values():
                for teaser in zeit.content.cp.interfaces.ITeaseredContent(
                        area):
                    counter = counter+1
    assert counter == 8


def test_dynamic_centerpage_should_be_paginatable(testserver, testbrowser):
    browser = testbrowser(
        '{}/dynamic/angela-merkel?p=2'.format(testserver.url))
    text = browser.cssselect('.pager__page.pager__page--current span')[0].text
    assert text == '2'


def test_centerpage_markdown_module_is_rendered(jinja2_env):
    tpl = jinja2_env.get_template('zeit.web.site:templates/centerpage.html')
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/thema')
    request = mock.MagicMock()
    request.route_url.return_value = 'http://foo.bar/'
    view = zeit.web.site.view_centerpage.Centerpage(content, request)
    html_str = tpl.render(view=view, request=request)
    html = lxml.html.fromstring(html_str)

    assert len(html.cssselect('.markup')) == 1
    assert len(html.cssselect('.markup__title')) == 1
    assert len(html.cssselect('.markup__text li')) == 4


def test_verlagsangebot_label_should_be_displayed(testbrowser):
    select = testbrowser('/zeit-online/teaser-inhouse-setup').cssselect
    labels = select('.teaser-small--inhouse .teaser-small__label')
    assert len(labels) == 2
    labels = select('.teaser-small-minor--inhouse .teaser-small-minor__label')
    assert len(labels) == 1
