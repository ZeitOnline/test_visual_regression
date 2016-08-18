# -*- coding: utf-8 -*-

import urllib2

import lxml.html
import pyramid.testing
import pytest
import zope.component

from zeit.cms.checkout.helper import checked_out
import zeit.cms.interfaces
import zeit.solr.interfaces

import zeit.web.site.view_centerpage

import babel
from datetime import datetime
from datetime import timedelta
from zeit.web.core.template import format_date


def get_num(x):
    return int(''.join(char for char in x.strip() if char.isdigit()))


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
    assert kicker and u'Flüchtlinge' in kicker[1].text
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


def test_buzzboard_renders_column_teaser(testbrowser):
    browser = testbrowser('/zeit-online/buzz-box')
    assert len(browser.cssselect('.teaser-buzzboard__media--column')) == 1
    assert len(browser.cssselect(
        '.teaser-buzzboard__media-container--column')) == 1


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
        testbrowser, workingcopy):
    uri = 'http://xml.zeit.de/angebote/print-box'
    content = zeit.cms.interfaces.ICMSContent(uri)
    with checked_out(content) as co:
        co.byline = 'mo-mi'
    browser = testbrowser('/zeit-online/index')
    printbox = browser.cssselect('.print-box:not(.print-box--angebot)')
    anbebotsbox = browser.cssselect('.print-box--angebot')

    assert len(printbox) == 0
    assert len(anbebotsbox) == 1


def test_printbox_is_present_and_has_newsprint_offerings(
        testbrowser, workingcopy):
    uri = 'http://xml.zeit.de/angebote/print-box'
    content = zeit.cms.interfaces.ICMSContent(uri)
    with checked_out(content) as co:
        co.byline = ''
    browser = testbrowser('/zeit-online/index')
    printbox = browser.cssselect('.print-box:not(.print-box--angebot)')
    anbebotsbox = browser.cssselect('.print-box--angebot')

    assert len(printbox) == 1
    assert len(anbebotsbox) == 0


def test_centerpage_should_gracefully_skip_all_broken_references(testbrowser):
    browser = testbrowser('/zeit-online/teaser-broken-setup')
    # @todo these class names are all gone
    assert not browser.cssselect('.main__fullwidth .teasers-fullwidth *')
    assert not browser.cssselect('.teaser-collection .teasers *')
    assert not browser.cssselect('.main__parquet .parquet *')
    assert not browser.cssselect('.main__snapshot *')


def test_dynamic_centerpage_collection_should_output_teasers(
        application, dummy_request):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{'uniqueId': ('http://xml.zeit.de/zeit-magazin/article/0%s'
                                  % i)}
                    for i in range(1, 9)]
    cp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/dynamic/ukraine')
    view = zeit.web.site.view_centerpage.Centerpage(cp, dummy_request)
    counter = 0
    for region in view.regions:
            for area in region.values():
                for teaser in zeit.content.cp.interfaces.ITeaseredContent(
                        area):
                    counter = counter + 1
    assert counter == 8


def test_dynamic_centerpage_should_be_paginatable(testbrowser, datasolr):
    browser = testbrowser('/dynamic/angela-merkel?p=2')
    current = browser.cssselect('.pager__page--current')[0]
    assert current.text_content().strip() == '2'


def test_pagination_should_be_validated(testbrowser):
    with pytest.raises(urllib2.HTTPError):
        assert '404 Not Found' in testbrowser(
            '/dynamic/angela-merkel?p=-1').headers
    with pytest.raises(urllib2.HTTPError):
        assert '404 Not Found' in testbrowser(
            '/dynamic/angela-merkel?p=0').headers
    with pytest.raises(urllib2.HTTPError):
        assert '404 Not Found' in testbrowser(
            '/dynamic/angela-merkel?p=1moep').headers


def test_centerpage_markdown_module_is_rendered(jinja2_env):
    tpl = jinja2_env.get_template('zeit.web.site:templates/centerpage.html')
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/thema')
    request = pyramid.testing.DummyRequest(
        route_url=lambda x: 'http://foo.bar/',
        asset_host='',
        image_host='')
    view = zeit.web.site.view_centerpage.Centerpage(content, request)
    view.meta_robots = ''
    view.canonical_url = ''
    html_str = tpl.render(view=view, request=request)
    html = lxml.html.fromstring(html_str)

    assert len(html.cssselect('.markup')) == 1
    assert len(html.cssselect('.markup__title')) == 1
    assert len(html.cssselect('.markup__text li')) == 4


def test_centerpage_teaser_topic_is_rendered(testbrowser):
    select = testbrowser('/zeit-online/topic-teaser').cssselect
    assert len(select('.teaser-topic')) == 1
    assert len(select('.teaser-topic__media')) == 1
    assert len(select('.teaser-topic-main')) == 1
    assert len(select('.teaser-topic-list')) == 1
    assert len(select('.teaser-topic-item')) == 3


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


def test_link_rel_should_be_set_according_to_pagination(testbrowser, datasolr):
    select = testbrowser('/dynamic/angela-merkel?p=3').cssselect
    rel_next = select('link[rel="next"]')
    rel_prev = select('link[rel="prev"]')
    assert len(rel_next) == 1
    assert len(rel_prev) == 1
    assert '/dynamic/angela-merkel?p=4' in rel_next[0].attrib['href']
    assert '/dynamic/angela-merkel?p=2' in rel_prev[0].attrib['href']


def test_link_rel_to_prev_page_should_not_exist_on_first_page(
        testbrowser, datasolr):
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
    box = driver.find_elements_by_css_selector(".overlay__dialog")[0]

    assert not wrap.is_displayed()
    assert not bg.is_displayed()
    assert not box.is_displayed()


def test_hp_shows_popover(selenium_driver, testserver):
    driver = selenium_driver

    # default
    driver.get('%s/index?force-popover' % testserver.url)

    wrap = driver.find_elements_by_css_selector("#overlay-wrapper")[0]
    bg = driver.find_elements_by_css_selector(".overlay")[0]
    box = driver.find_elements_by_css_selector(".overlay__dialog")[0]

    assert wrap.is_displayed()
    assert bg.is_displayed()
    assert box.is_displayed()


def test_zon_campus_teaser_fullwidth_has_campus_signet(testbrowser):
    select = testbrowser('zeit-online/centerpage/teasers-to-campus').cssselect
    svg = select('.teaser-fullwidth .teaser-fullwidth__kicker-logo--zco')
    assert svg[0].xpath('title')[0].text == 'ZEIT Campus'


def test_zon_campus_teaser_large_has_campus_signet(testbrowser):
    select = testbrowser('zeit-online/centerpage/teasers-to-campus').cssselect
    teaser = select('.teaser-large')
    svg = select('.teaser-large .teaser-large__kicker-logo--zco')
    # 4 teaser, but only 3 sighnets
    assert len(teaser) == 4
    assert len(svg) == 3
    # main
    assert svg[0].xpath('title')[0].text == 'ZEIT Campus'
    # column
    assert svg[1].xpath('title')[0].text == 'ZEIT Campus'
    # parquet
    assert svg[2].xpath('title')[0].text == 'ZEIT Campus'


def test_zon_campus_teaser_small_has_campus_signet(testbrowser):
    select = testbrowser('zeit-online/centerpage/teasers-to-campus').cssselect
    teaser = select('.teaser-small')
    svg = select('.teaser-small .teaser-small__kicker-logo--zco')
    # 4 teaser, but only 3 sighnets
    assert len(teaser) == 4
    assert len(svg) == 3
    # main
    assert svg[0].xpath('title')[0].text == 'ZEIT Campus'
    # column
    assert svg[1].xpath('title')[0].text == 'ZEIT Campus'
    # parquet
    assert svg[2].xpath('title')[0].text == 'ZEIT Campus'


def test_zon_campus_teaser_column_has_default_layout(testbrowser):
    select = testbrowser('zeit-online/centerpage/teasers-to-campus').cssselect
    assert len(select('.teaser-large-column')) == 0
    assert len(select('.teaser-small-column')) == 0
    assert len(select('.teaser-minor-column')) == 0


def test_zon_campus_teaser_small_minor_has_campus_signet(testbrowser):
    select = testbrowser('zeit-online/centerpage/teasers-to-campus').cssselect
    teaser = '.teaser-small-minor'
    logo = '.teaser-small-minor__kicker-logo--zco'
    svg = select('{} {}'.format(teaser, logo))
    assert svg[0].xpath('title')[0].text == 'ZEIT Campus'


def test_zon_campus_teaser_topic_has_campus_signet(testbrowser):
    select = testbrowser('zeit-online/centerpage/teasers-to-campus').cssselect
    teaser = select('.teaser-topic-item')
    svg = select('.teaser-topic-item__kicker-logo--zco')
    # 4 teaser, but only 3 sighnets
    assert len(teaser) == 3
    assert len(svg) == 3
    assert svg[0].xpath('title')[0].text == 'ZEIT Campus'
    assert svg[1].xpath('title')[0].text == 'ZEIT Campus'
    assert svg[2].xpath('title')[0].text == 'ZEIT Campus'


def test_liveblog_teaser_respects_liveblog_status(testbrowser):
    browser = testbrowser('zeit-online/centerpage/liveblog')
    main = browser.cssselect('main.main')[0]
    liveblog = main.cssselect('span[class*="__kicker-logo--liveblog"]')
    offline = main.cssselect('span[class*="__kicker-logo--liveblog-closed"]')

    assert len(liveblog) == 17
    assert len(offline) == 8


def test_format_date_returns_expected_value_in_newsbox():
    tz = babel.dates.get_timezone('Europe/Berlin')
    now = datetime.now(tz)
    before = now - timedelta(hours=5)
    yesterday = now - timedelta(days=1)

    assert 'Heute, ' + str(before.strftime('%H:%M'))\
        == format_date(before, type="switch_from_hours_to_date")

    day = str(yesterday.strftime('%d'))
    assert day.lstrip('0') + '. ' + str(yesterday.strftime('%m. %Y')) \
        == format_date(yesterday, type="switch_from_hours_to_date")

    assert str(yesterday.strftime('%H:%M'))\
        == format_date(yesterday, pattern="HH:mm")


def test_newsbox_renders_correctly_on_homepage(testbrowser, datasolr):
    browser = testbrowser('/zeit-online/slenderized-index-with-newsbox')
    wrapper = browser.cssselect('.newsticker__column')
    section_heading_link = browser.cssselect('.section-heading__link')
    assert len(wrapper) == 2
    assert len(section_heading_link) == 1


def test_newsbox_renders_correctly_on_keywordpage(testbrowser, datasolr):
    browser = testbrowser('/thema/oper')
    wrapper = browser.cssselect('.newsticker__single')
    newsbox = browser.cssselect(
        '.cp-area--newsticker'
        '.cp-area--newsticker-on-keywordpage')
    linktext = browser.cssselect('.newsteaser__text--kw-tp-page')
    section_heading_link = browser.cssselect('.section-heading__link')
    assert len(wrapper) == 1
    assert len(newsbox) == 1
    assert len(linktext) >= 1
    assert len(section_heading_link) == 0
