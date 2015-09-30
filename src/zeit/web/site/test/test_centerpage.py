# -*- coding: utf-8 -*-

import datetime
import urllib2

import lxml.html
import pyramid.testing
import pysolr
import pytest

import zeit.cms.interfaces
from zeit.cms.checkout.helper import checked_out

import zeit.web.site.view_centerpage


def get_num(x):
    return int(''.join(char for char in x.strip() if char.isdigit()))


def test_centerpage_has_last_semantic_change_property(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/centerpage/zeitonline')
    view = zeit.web.site.view_centerpage.Centerpage(
        context, pyramid.testing.DummyRequest())

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
    kicker = browser.cssselect('.buzz-box--mostread .teaser-buzz__kicker')
    titles = browser.cssselect('.buzz-box--mostread .teaser-buzz__title')
    assert kicker and u'Asylbewerber' in kicker[1].text
    assert titles and u'Fluchthilfe ganz privat' in titles[2].text


def test_buzz_comments_should_render_correct_article_count(testbrowser):
    browser = testbrowser('/zeit-online/buzz-box')
    articles = browser.cssselect('.buzz-box--comments article.teaser-buzz')
    assert len(articles) == 3


def test_buzz_comments_should_render_with_correct_scores(testbrowser):
    browser = testbrowser('/zeit-online/buzz-box')
    media = browser.cssselect('.buzz-box--comments .teaser-buzz__metadata')
    assert [get_num(m.text_content()) for m in media] == [531, 461, 265]


def test_buzz_comments_should_output_correct_titles(testbrowser):
    browser = testbrowser('/zeit-online/buzz-box')
    kicker = browser.cssselect('.buzz-box--comments .teaser-buzz__kicker')
    titles = browser.cssselect('.buzz-box--comments .teaser-buzz__title')
    assert u'Asylbewerber' in kicker[0].text
    assert u'Orbán verlangt Schließung der Grenzen' in titles[2].text


def test_buzz_mostshared_should_render_correct_article_count(testbrowser):
    browser = testbrowser('/zeit-online/buzz-box')
    articles = browser.cssselect('.buzz-box--shared article.teaser-buzz')
    assert len(articles) == 3


def test_buzz_mostshared_should_render_with_correct_scores(testbrowser):
    browser = testbrowser('/zeit-online/buzz-box')
    media = browser.cssselect('.buzz-box--shared .teaser-buzz__metadata')
    assert [get_num(m.text_content()) for m in media] == [2357, 2346, 1227]


def test_buzz_mostshared_should_output_correct_titles(testbrowser):
    browser = testbrowser('/zeit-online/buzz-box')
    kicker = browser.cssselect('.buzz-box--shared .teaser-buzz__kicker')
    titles = browser.cssselect('.buzz-box--shared .teaser-buzz__title')
    assert u'Studienwahl' in kicker[0].text
    assert u'Zuwanderer haben häufiger Abitur' in titles[1].text


def test_buzzboard_renders(testbrowser):
    browser = testbrowser('/zeit-online/buzz-box')
    area = browser.cssselect('.cp-area--buzzboard')
    assert len(area) == 1
    board = area[0].cssselect('.buzzboard__table')
    assert len(board) == 1
    images = board[0].cssselect('.teaser-buzzboard__media')
    assert len(images) == 4


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
    view = zeit.web.site.view_centerpage.Centerpage(
        cp, pyramid.testing.DummyRequest())
    counter = 0
    for region in view.regions:
            for area in region.values():
                for teaser in zeit.content.cp.interfaces.ITeaseredContent(
                        area):
                    counter = counter + 1
    assert counter == 8


def test_dynamic_centerpage_should_be_paginatable(testserver, testbrowser):
    browser = testbrowser(
        '{}/dynamic/angela-merkel?p=2'.format(testserver.url))
    text = browser.cssselect('.pager__page.pager__page--current span')[0].text
    assert text == '2'


def test_pagination_should_be_validated(testserver, testbrowser):
    with pytest.raises(urllib2.HTTPError):
        assert '404 Not Found' in testbrowser(
            '{}/dynamic/angela-merkel?p=-1'.format(testserver.url)).headers
    with pytest.raises(urllib2.HTTPError):
        assert '404 Not Found' in testbrowser(
            '{}/dynamic/angela-merkel?p=123'.format(testserver.url)).headers
    with pytest.raises(urllib2.HTTPError):
        assert '404 Not Found' in testbrowser(
            '{}/dynamic/angela-merkel?p=1moep'.format(testserver.url)).headers


def test_centerpage_markdown_module_is_rendered(jinja2_env):
    tpl = jinja2_env.get_template('zeit.web.site:templates/centerpage.html')
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/thema')
    request = pyramid.testing.DummyRequest(
        route_url=lambda x: 'http://foo.bar/',
        asset_url=lambda x: '',
        image_host='')
    view = zeit.web.site.view_centerpage.Centerpage(content, request)
    view.meta_robots = ''
    view.canonical_url = ''
    html_str = tpl.render(view=view, request=request)
    html = lxml.html.fromstring(html_str)

    assert len(html.cssselect('.markup')) == 1
    assert len(html.cssselect('.markup__title')) == 1
    assert len(html.cssselect('.markup__text li')) == 4


def test_centerpage_teaser_topic_is_rendered(jinja2_env):
    tpl = jinja2_env.get_template('zeit.web.site:templates/centerpage.html')
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/topic-teaser')
    request = pyramid.testing.DummyRequest(
        route_url=lambda x: 'http://foo.bar/',
        asset_url=lambda x: '',
        image_host='')
    request.route_url.return_value = 'http://foo.bar/'
    view = zeit.web.site.view_centerpage.Centerpage(content, request)
    view.meta_robots = ''
    view.canonical_url = ''
    html_str = tpl.render(view=view, request=request)
    html = lxml.html.fromstring(html_str)

    assert len(html.cssselect('.teaser-topic')) == 1
    assert len(html.cssselect('.teaser-topic-main')) == 1
    assert len(html.cssselect('.teaser-topic-item')) == 3


def test_inhouse_label_should_be_displayed(testbrowser):
    select = testbrowser('/zeit-online/teaser-inhouse-setup').cssselect
    labels = select('.teaser-small--inhouse .teaser-small__label')
    assert len(labels) == 2
    assert map(lambda x: x.text, labels) == (
        ['Verlagsangebot', 'Verlagsangebot'])


def test_ad_label_should_be_displayed(testbrowser):
    select = testbrowser('/zeit-online/teaser-inhouse-setup').cssselect
    labels = select('.teaser-small-minor--ad .teaser-small-minor__label')
    assert len(labels) == 1
    assert labels[0].text == 'Anzeige'


def test_link_rel_should_be_set_according_to_pagination(testbrowser):
    select = testbrowser('/dynamic/angela-merkel?p=3').cssselect
    rel_next = select('link[rel="next"]')
    rel_prev = select('link[rel="prev"]')
    assert len(rel_next) == 1
    assert len(rel_prev) == 1
    assert '/dynamic/angela-merkel?p=4' in rel_next[0].attrib['href']
    assert '/dynamic/angela-merkel?p=2' in rel_prev[0].attrib['href']


def test_link_rel_to_prev_page_should_not_exist_on_first_page(testbrowser):
    select = testbrowser('/dynamic/angela-merkel').cssselect
    rel_next = select('link[rel="next"]')
    rel_prev = select('link[rel="prev"]')
    assert len(rel_next) == 1
    assert len(rel_prev) == 0
    assert '/dynamic/angela-merkel?p=2' in rel_next[0].attrib['href']


def test_hp_hides_popover_per_default(selenium_driver, testserver):
    driver = selenium_driver

    # default
    driver.get('%s/index?debug-popover' % testserver.url)

    wrap = driver.find_elements_by_css_selector("#overlay-wrapper")[0]
    bg = driver.find_elements_by_css_selector(".overlay")[0]
    box = driver.find_elements_by_css_selector(".lightbox")[0]

    assert not wrap.is_displayed()
    assert not bg.is_displayed()
    assert not box.is_displayed()


def test_hp_shows_popover(selenium_driver, testserver):
    driver = selenium_driver

    # default
    driver.get('%s/index?force-popover' % testserver.url)

    wrap = driver.find_elements_by_css_selector("#overlay-wrapper")[0]
    bg = driver.find_elements_by_css_selector(".overlay")[0]
    box = driver.find_elements_by_css_selector(".lightbox")[0]

    assert wrap.is_displayed()
    assert bg.is_displayed()
    assert box.is_displayed()
