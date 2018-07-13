# -*- coding: utf-8 -*-
import datetime
import urllib2

import lxml.html
import pytest
import zope.component

from zeit.cms.checkout.helper import checked_out
import zeit.cms.interfaces
import zeit.solr.interfaces

import zeit.web.site.view_centerpage

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
    assert 'Arbeitswelt' == kicker[2].text.strip()
    assert 'Der Terror der guten Laune' == titles[2].text


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
    assert 'Steuerhinterziehung' == kicker[0].text.strip()
    assert u'"Die Schweiz ist die größte Fluchtburg"' == titles[0].text


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
    assert 'Gender Studies' == kicker[0].text.strip()
    assert 'Born to be wild' == titles[1].text


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


def test_buzzboard_renders_column_teaser_without_authorimage(testbrowser):
    browser = testbrowser('/zeit-online/buzz-box')
    url = 'http://xml.zeit.de/zeit-online/cp-content/kolumne-ohne-autorenbild'
    article = browser.cssselect(
        'article.teaser-buzzboard[data-unique-id="{}"]'.format(url))[0]
    assert article.cssselect('.teaser-buzzboard__media')
    assert not article.cssselect('.teaser-buzzboard__media--column')
    assert article.cssselect('.teaser-buzzboard__media-container')
    assert not article.cssselect('.teaser-buzzboard__media-container--column')


def test_buzzboard_should_avoid_same_teaser_image_twice(
        testbrowser, monkeypatch):

    # Make most shared equal to most read to provide two column teasers.
    def social_ranking(self, **kw):
        return self._get_ranking('views', **kw)

    monkeypatch.setattr(
        zeit.web.core.reach.Reach, 'get_social', social_ranking)

    browser = testbrowser('/zeit-online/buzz-box')
    area = browser.cssselect('.cp-area--buzzboard')[0]
    assert len(area.cssselect('.teaser-buzzboard__media')) == 4
    assert len(area.cssselect('.teaser-buzzboard__media--duplicate')) == 1


def test_printbox_is_present_and_has_digital_offerings(
        testbrowser, workingcopy):
    uri = 'http://xml.zeit.de/angebote/print-box'
    content = zeit.cms.interfaces.ICMSContent(uri)
    with checked_out(content) as co:
        co.byline = 'mo-mi'
    browser = testbrowser('/zeit-online/printbox')
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
    browser = testbrowser('/zeit-online/printbox')
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


def test_dynamic_centerpage_should_be_paginatable(testbrowser, data_solr):
    browser = testbrowser('/dynamic/angela-merkel?p=2')
    current = browser.cssselect('.pager__page--current')[0]
    assert current.text_content().strip() == '2'


def test_dynamic_centerpage_paginator_has_https_links(testbrowser, data_solr):
    zeit.web.core.application.FEATURE_TOGGLES.unset('https')
    browser = testbrowser('/dynamic/angela-merkel?p=2')
    current = browser.cssselect('.pager__page a')[0]
    assert 'http://' in current.attrib.get('href')

    zeit.web.core.application.FEATURE_TOGGLES.set('https')
    browser = testbrowser('/dynamic/angela-merkel?p=2')
    current = browser.cssselect('.pager__page a')[0]
    assert 'https://' in current.attrib.get('href')


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


def test_centerpage_markdown_module_is_rendered(jinja2_env, dummy_request):
    tpl = jinja2_env.get_template('zeit.web.site:templates/centerpage.html')
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/thema')
    view = zeit.web.site.view_centerpage.Centerpage(content, dummy_request)
    view.meta_robots = ''
    view.canonical_url = ''
    html_str = tpl.render(view=view, request=dummy_request)
    html = lxml.html.fromstring(html_str)

    assert len(html.cssselect('.markup')) == 1
    assert len(html.cssselect('.markup__title')) == 1
    assert len(html.cssselect('.markup__text li')) == 4


def test_centerpage_teaser_topic_has_correct_structure(testbrowser):
    browser = testbrowser('/zeit-online/topic-teaser')
    teaser = browser.cssselect('.teaser-topic')[0]
    image = teaser.cssselect('.teaser-topic__media-item')[0]

    assert len(teaser.cssselect('.teaser-topic__media')) == 1
    assert len(teaser.cssselect('.teaser-topic-main')) == 1
    assert len(teaser.cssselect('.teaser-topic-list')) == 1
    assert len(teaser.cssselect('.teaser-topic-item')) == 3

    assert image.get('data-src').endswith(
        '/zeit-online/cp-content/ig-1/cinema')
    assert image.get('data-mobile-src').endswith(
        '/zeit-online/cp-content/ig-1/portrait')


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


def test_link_rel_should_be_set_according_to_pagination(
        testbrowser, data_solr):
    select = testbrowser('/dynamic/angela-merkel?p=3').cssselect
    rel_next = select('link[rel="next"]')
    rel_prev = select('link[rel="prev"]')
    assert len(rel_next) == 1
    assert len(rel_prev) == 1
    assert '/dynamic/angela-merkel?p=4' in rel_next[0].get('href')
    assert '/dynamic/angela-merkel?p=2' in rel_prev[0].get('href')


def test_link_rel_to_prev_page_should_not_exist_on_first_page(
        testbrowser, data_solr):
    select = testbrowser('/dynamic/angela-merkel').cssselect
    rel_next = select('link[rel="next"]')
    rel_prev = select('link[rel="prev"]')
    assert len(rel_next) == 1
    assert len(rel_prev) == 0
    assert '/dynamic/angela-merkel?p=2' in rel_next[0].get('href')


def test_hp_hides_popover_per_default(selenium_driver, testserver):
    driver = selenium_driver

    # default
    driver.get('{}/zeit-online/slenderized-index?debug-popover'.format(
        testserver.url))

    wrap = driver.find_elements_by_css_selector("#overlay-wrapper")[0]
    bg = driver.find_elements_by_css_selector(".overlay")[0]
    box = driver.find_elements_by_css_selector(".overlay__dialog")[0]

    assert not wrap.is_displayed()
    assert not bg.is_displayed()
    assert not box.is_displayed()


def test_hp_shows_popover(selenium_driver, testserver):
    driver = selenium_driver

    # default
    driver.get('{}/zeit-online/slenderized-index?force-popover'.format(
        testserver.url))

    wrap = driver.find_elements_by_css_selector("#overlay-wrapper")[0]
    bg = driver.find_elements_by_css_selector(".overlay")[0]
    box = driver.find_elements_by_css_selector(".overlay__dialog")[0]

    assert wrap.is_displayed()
    assert bg.is_displayed()
    assert box.is_displayed()


def test_hp_shows_alternative_popover(selenium_driver, testserver):
    driver = selenium_driver

    # default
    driver.get('{}/zeit-online/slenderized-index?force-popover'.format(
        testserver.url))

    text = driver.find_element_by_css_selector(".overlay__text")
    assert text.is_displayed()

    # alternative popover hides text, so after running the script
    # -> the text should not be shown

    script = 'arguments[0].classList.add("overlay-wrapper--alternative");'
    element = driver.find_element_by_css_selector('#overlay-wrapper')
    driver.execute_script(script, element)
    text = driver.find_element_by_css_selector(".overlay__text")
    assert not text.is_displayed()


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

    assert len(liveblog) == 21
    assert len(offline) == 10


def test_format_date_returns_expected_value_in_newsbox(clock):
    # we tell the test that it is currently 14 o clock in June 2015
    # (to be indepentent from the actual runtime)
    clock.freeze(datetime.datetime(2015, 6, 1, 14, 0))

    date_today = datetime.datetime(2015, 6, 1, 10, 21)
    assert 'Heute, 10:21' == format_date(
        date_today, type='switch_from_hours_to_date')
    assert '10:21' == format_date(
        date_today, pattern='HH:mm')

    date_yesterday_less_than_24h_ago = datetime.datetime(2015, 5, 31, 18, 2)
    assert '31. 05. 2015' == format_date(
        date_yesterday_less_than_24h_ago, type='switch_from_hours_to_date')
    assert '18:02' == format_date(
        date_yesterday_less_than_24h_ago, pattern='HH:mm')

    date_yesterday_more_than_24h_ago = datetime.datetime(2015, 5, 31, 9, 30)
    assert '31. 05. 2015' == format_date(
        date_yesterday_more_than_24h_ago, type='switch_from_hours_to_date')
    assert '09:30' == format_date(
        date_yesterday_more_than_24h_ago, pattern='HH:mm')

    date_long_time_ago = datetime.datetime(2015, 4, 3, 1, 52)
    assert '03. 04. 2015' == format_date(
        date_long_time_ago, type='switch_from_hours_to_date')
    assert '01:52' == format_date(
        date_long_time_ago, pattern='HH:mm')


def test_newsbox_renders_correctly_on_homepage(testbrowser, data_solr):
    browser = testbrowser('/zeit-online/slenderized-index-with-newsbox')
    wrapper = browser.cssselect('.newsticker__column')
    section_heading_link = browser.cssselect('.section-heading__link')
    assert len(wrapper) == 2
    assert len(section_heading_link) == 1


def test_newsbox_renders_correctly_on_auto_topicpage(testbrowser, data_solr):
    browser = testbrowser('/thema/oper')
    newsbox = browser.cssselect(
        '.cp-area--newsticker.cp-area--newsticker-on-autotopic')
    linktext = browser.cssselect('.newsteaser__text--on-autotopic')
    section_heading_link = browser.cssselect('.section-heading__link')
    assert len(newsbox) == 1
    assert len(linktext) == 8
    assert len(section_heading_link) == 0


def test_newsbox_renders_correctly_on_manual_topicpage(testbrowser, data_solr):
    browser = testbrowser('/thema/jurastudium')
    newsbox = browser.cssselect(
        '.cp-area--newsticker.cp-area--newsticker-on-manualtopic')
    linktext = browser.cssselect('.newsteaser__text--on-manualtopic')
    section_heading_link = browser.cssselect('.section-heading__link')
    assert len(newsbox) == 1
    assert len(linktext) == 8
    assert len(section_heading_link) == 0


def test_zon_arbeit_teaser_fullwidth_has_arbeit_signet(testbrowser):
    select = testbrowser('zeit-online/centerpage/teasers-to-arbeit').cssselect
    svg = select('.teaser-fullwidth .teaser-fullwidth__kicker-logo--zar')
    assert len(svg) == 1


def test_zon_arbeit_teaser_large_has_arbeit_signet(testbrowser):
    select = testbrowser('zeit-online/centerpage/teasers-to-arbeit').cssselect
    teaser = select('.teaser-large')
    svg = select('.teaser-large .teaser-large__kicker-logo--zar')
    assert len(teaser) == 2
    assert len(svg) == 2


def test_zon_arbeit_teaser_small_has_arbeit_signet(testbrowser):
    select = testbrowser('zeit-online/centerpage/teasers-to-arbeit').cssselect
    teaser = select('.teaser-small')
    svg = select('.teaser-small__kicker-logo--zar')
    teaser_in_minor = select('.teaser-small-minor')
    svg_in_minor = select('.teaser-small-minor__kicker-logo--zar')
    assert len(teaser) == 4
    assert len(svg) == 4
    assert len(teaser_in_minor) == 2
    assert len(svg_in_minor) == 2


def test_zon_arbeit_teaser_small_minor_has_arbeit_signet(testbrowser):
    select = testbrowser('zeit-online/centerpage/teasers-to-arbeit').cssselect
    teaser = select('.teaser-small-minor')
    svg = select('.teaser-small-minor .teaser-small-minor__kicker-logo--zar')
    assert len(teaser) == 2
    assert len(svg) == 2


def test_zon_arbeit_teaser_topic_has_arbeit_signet(testbrowser):
    select = testbrowser('zeit-online/centerpage/teasers-to-arbeit').cssselect
    teaser = select('.teaser-topic-item')
    svg = select('.teaser-topic-item__kicker-logo--zar')
    assert len(teaser) == 3
    assert len(svg) == 3


def test_if_all_followbox_elements_present(testbrowser):
    select = testbrowser('zeit-online/centerpage/follow-us').cssselect
    buttons = select('.follow-us__link')

    assert len(buttons) == 5
