import re
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

import zope.component
import zeit.solr.interfaces

# import zeit.cms.interfaces

# import zeit.web.core.interfaces

import zeit.web.campus.view_centerpage


def test_campus_navigation_should_present_flyout(selenium_driver, testserver):
    driver = selenium_driver
    # assert desktop breakpoint
    driver.set_window_size(1024, 768)
    driver.get('%s/campus/index' % testserver.url)
    link = driver.find_element_by_css_selector(
        '.nav__tools-title .nav__dropdown')
    link.click()
    try:
        WebDriverWait(driver, 5).until(
            expected_conditions.presence_of_element_located(
                (By.CLASS_NAME, 'nav-flyout')))
    except TimeoutException:
        assert False, 'Navigation flyout not visible within 5 seconds'
    else:
        flyout = driver.find_elements_by_css_selector(
            '#tools-menu .nav-flyout__item')
        assert len(flyout) == 3
        link.click()
        try:
            WebDriverWait(driver, 5).until(
                expected_conditions.invisibility_of_element_located(
                    (By.ID, 'tools-menu')))
        except TimeoutException:
            assert False, 'Navigation flyout not hidden within 5 seconds'
        else:
            assert True


def test_campus_teaser_wide_small_should_not_display_its_image_on_mobile(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.set_window_size(320, 480)
    driver.get('%s/campus/centerpage/teaser-wide-small' % testserver.url)
    teaser_images = driver.find_elements_by_class_name(
        'teaser-wide-small__media')

    for image in teaser_images:
        assert ('teaser-wide-small__media--force-mobile' in
                image.get_attribute('class')) or (not image.is_displayed())

    driver.set_window_size(768, 800)
    for image in teaser_images:
        assert image.is_displayed()


def test_campus_teaser_wide_small_has_correct_structure(testbrowser):
    select = testbrowser('/campus/centerpage/teaser-wide-small').cssselect

    assert len(select('.teaser-wide-small')) == 3
    assert len(select('.teaser-wide-small__metadata')) == 3
    assert len(select('.teaser-wide-small__byline')) == 3
    assert len(select('.teaser-wide-small__content')) == 0

    byline = select('.teaser-wide-small__byline')[2]
    byline_text = re.sub('\s+', ' ', byline.text_content().strip())
    assert byline_text == 'Von Viola Diem'


def test_campus_teaser_wide_large_has_correct_structure(testbrowser):
    select = testbrowser('/campus/centerpage/teaser-wide-large').cssselect

    assert len(select('.teaser-wide-large')) == 2
    assert len(select(
        '.teaser-wide-large .teaser-wide-large__heading '
        '.teaser-wide-large__kicker')) == 2
    assert len(select(
        '.teaser-wide-large .teaser-wide-large__heading '
        '.teaser-wide-large__title')) == 2

    assert len(select('.teaser-wide-large__metadata')) == 2
    assert len(select('.teaser-wide-large__byline')) == 2
    assert len(select('.teaser-wide-large__content')) == 0


def test_campus_teaser_square_exists(testbrowser):
    select = testbrowser('/campus/centerpage/teaser-square').cssselect
    assert len(select('.teaser-square')) == 4


def test_campus_teaser_lead_portrait_has_correct_structure(testbrowser):
    select = testbrowser('/campus/centerpage/teaser-lead-portrait').cssselect
    assert len(select('.teaser-lead-portrait')) == 1
    assert len(select(
        '.teaser-lead-portrait .teaser-lead-portrait__content '
        '.teaser-lead-portrait__heading .teaser-lead-portrait__title')) == 1
    assert len(select('.teaser-lead-portrait__metadata')) == 1


def test_campus_teaser_lead_cinema_has_correct_structure(testbrowser):
    select = testbrowser('/campus/centerpage/teaser-lead-cinema').cssselect
    assert len(select('.teaser-lead-cinema')) == 1
    assert len(select('.teaser-lead-cinema__content')) == 0
    assert len(select('.teaser-lead-cinema__metadata')) == 1


def test_campus_teaser_topic_has_correct_structure(testbrowser):
    browser = testbrowser('/campus/centerpage/teaser-topic')
    teaser = browser.cssselect('.teaser-topic')[0]
    image = teaser.cssselect('.teaser-topic__media-item')[0]

    assert len(teaser.cssselect('.teaser-topic__media')) == 1
    assert len(teaser.cssselect('.teaser-topic-main')) == 1
    assert len(teaser.cssselect('.teaser-topic-list')) == 1
    assert len(teaser.cssselect('.teaser-topic-item')) == 3

    assert image.attrib['data-src'].endswith(
        '/zeit-online/cp-content/ig-1/cinema')
    assert image.attrib['data-mobile-src'].endswith(
        '/zeit-online/cp-content/ig-1/portrait')


def test_campus_teaser_topic_variant_has_correct_structure(testbrowser):
    browser = testbrowser('/campus/centerpage/teaser-topic-variant')
    select = browser.cssselect('.teaser-topic-variant')[0].cssselect
    assert len(select('.teaser-topic-variant-list')) == 1
    assert len(select('.teaser-topic-variant__media-container')) == 1
    assert len(select('.teaser-topic-variant__media-container a')) == 1
    assert len(select('.teaser-topic-wide')) == 1
    assert len(select('.teaser-topic-wide__topic-button')) == 1
    assert len(select('.teaser-topic-small')) == 2
    assert (
        'cp-content/ig-2/portrait__612x816' in
        select('.teaser-topic-variant__media-item').pop().attrib['src'])


def test_campus_teaser_debate_has_correct_structure(testbrowser):
    select = testbrowser('/campus/centerpage/teaser-debate').cssselect
    assert len(select('.teaser-debate')) == 1
    assert len(select('.debate')) == 1
    assert len(select('.debate__kicker')) == 1
    assert len(select('.debate__title')) == 1
    assert len(select('.debate__text')) == 1
    assert len(select('.debate__label')) == 1
    assert (select('.debate__kicker')[0].text_content().strip() ==
            'Das steht zur Debatte')


def test_campus_toolbox_exists(testbrowser):
    select = testbrowser('/campus/centerpage/cp-extra-tool-box').cssselect
    assert len(select('.toolbox')) == 1
    assert len(select('.toolbox__headline')) == 1
    assert len(select('.toolbox__item')) == 2


def test_campus_navigation_contains_jobmarket(testbrowser):
    browser = testbrowser('/campus/article/simple')
    jobmarket = browser.cssselect('.nav__tools')[1]
    assert len(jobmarket.cssselect('.nav__tools-title')) == 1
    assert len(jobmarket.cssselect('.nav__tools-list a')) == 2
    control = jobmarket.cssselect('a[aria-controls]')[0]
    flyout = browser.cssselect('#%s' % control.get('aria-controls'))[0]
    assert len(flyout.cssselect('.nav-flyout__link')) == 2
    assert len(flyout.cssselect('.nav-flyout__footer-link')) == 1


def test_headerimage_has_appropriate_html_structure(testbrowser):
    browser = testbrowser('/campus/centerpage/thema')
    header = browser.cssselect('.header-image')
    image = header[0].cssselect('.header-image__media-item')[0]
    assert len(header[0].cssselect('.header-image__heading--overlay')) == 1
    assert len(header[2].cssselect('.header-image__heading--overlay')) == 0
    assert image.get('data-ratio') == '2.33333333333'  # variant=cinema
    assert not image.get('data-mobile-ratio')


def test_advertorial_header_has_appropriate_html_structure(testbrowser):
    select = testbrowser('/campus/centerpage/advertorial').cssselect
    assert len(select('.header-image')) == 1
    assert len(select('.header-advertorial__heading')) == 1
    assert len(select('.header-advertorial__kicker')) == 1
    assert len(select('.header-advertorial__title')) == 1


def test_advertorial_has_markup_module(testbrowser):
    select = testbrowser('/campus/centerpage/advertorial').cssselect
    assert len(select('.markup')) == 1


def test_servicelinks_module_renders_links(testbrowser):
    select = testbrowser('/campus/centerpage/servicelinks').cssselect
    assert len(select('.servicelinks a.servicelinks__link')) == 6


def test_campus_teasers_to_leserartikel_have_kicker_modifiers(testbrowser):
    select = testbrowser(
        '/campus/centerpage/teasers-to-leserartikel').cssselect
    assert len(select(
        '[class^="teaser"][class*="__kicker--leserartikel"]')) == 9

    select = testbrowser(
        '/campus/article/simple-with-nextread-leserartikel').cssselect
    assert len(select('.nextread-teaser__kicker--leserartikel')) == 1


def test_campus_cp_page_integration(testbrowser, datasolr):
    browser = testbrowser('/campus/centerpage/paginierung?p=2')
    # Curated content is not shown
    assert 'Ich bin nicht intellektuell' not in browser.contents
    # Header is kept
    assert 'class="header-image"' in browser.contents
    # Ranking is kept
    assert 'cp-area--zco-ranking' in browser.contents


def test_campus_teaser_no_image_fallback_works_as_expected(testbrowser):
    select = testbrowser('/campus/centerpage/index-noimage').cssselect
    assert (
        '/default/teaser_image/' in
        select('.teaser-lead-portrait__media-item')[0].attrib['src'])
    assert (
        '/campus/image/01-junge-vor-unscharfem-hintergrund/' in
        select('.teaser-lead-portrait__media-item')[1].attrib['src'])
    assert (
        '/default/teaser_image/' in
        select('.teaser-lead-cinema__media-item')[0].attrib['src'])
    assert (
        '/campus/image/02-maedchen-koffer-zug/' in
        select('.teaser-lead-cinema__media-item')[1].attrib['src'])
    assert (
        '/default/teaser_image/' in
        select('.teaser-lead-cinema__media-item')[2].attrib['src'])
    assert (
        '/default/teaser_image/' in
        select('.teaser-wide-large__media-item')[0].attrib['src'])
    assert (
        '/campus/image/02-maedchen-koffer-zug/' in
        select('.teaser-wide-large__media-item')[1].attrib['src'])
    assert (
        '/default/teaser_image/' in
        select('.teaser-wide-small__media-item')[0].attrib['src'])
    assert (
        '/campus/image/02-maedchen-koffer-zug/' in
        select('.teaser-wide-small__media-item')[1].attrib['src'])
    assert (
        '/default/teaser_image/' in
        select('.teaser-square__media-item')[0].attrib['src'])
    assert (
        '/campus/image/01-junge-vor-unscharfem-hintergrund/' in
        select('.teaser-square__media-item')[1].attrib['src'])
    assert (
        '/default/teaser_image/' in
        select('.teaser-graphical__media-item')[0].attrib['src'])
    assert (
        '/campus/image/01-junge-vor-unscharfem-hintergrund/' in
        select('.teaser-graphical__media-item')[1].attrib['src'])
    assert (
        '/default/teaser_image/' in
        select('.teaser-topic-variant__media-item')[0].attrib['src'])
    assert (
        '/default/teaser_image/' in
        select('.teaser-topic-small__media-item')[0].attrib['src'])
    assert (
        '/campus/image/02-maedchen-koffer-zug/' in
        select('.teaser-topic-small__media-item')[1].attrib['src'])
    assert (
        '/default/teaser_image/' in
        select('.packshot__media-item')[0].attrib['src'])
    assert (
        '/campus/image/cover/' in
        select('.packshot__media-item')[1].attrib['src'])


def test_campus_advertorial_teaser(testbrowser):
    select = testbrowser(
        '/campus/centerpage/teaser-advertorial').cssselect
    assert len(select('.teaser-wide-small--advertorial')) == 2


def test_paginated_cp_has_correct_teaser_structure(testbrowser):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/01'}]
    browser = testbrowser('/campus/centerpage/paginierung?p=2')
    teaser = browser.cssselect('.teaser-small')[0]
    image = teaser.cssselect('.teaser-small__media-item')[0]
    assert len(teaser.cssselect('.teaser-small__media')) == 1
    assert len(teaser.cssselect('.teaser-small__content')) == 1
    assert image.get('data-ratio') == '1.77777777778'


def test_campus_toolbox_has_correct_links(testbrowser):
    select = testbrowser('/campus/centerpage/cp-extra-tool-box').cssselect
    assert ('http://studiengaenge.zeit.de/sit' in
            select('.toolbox__link')[0].attrib['href'])
    assert ('https://jobs.zeit.de/campus/berufstest' in
            select('.toolbox__link')[1].attrib['href'])


def test_campus_flyout_has_correct_links(selenium_driver, testserver):
    driver = selenium_driver
    # assert desktop breakpoint
    driver.set_window_size(1024, 768)
    driver.get('%s/campus/index' % testserver.url)
    link = driver.find_element_by_css_selector(
        '.nav__tools-title .nav__dropdown')
    link.click()
    try:
        WebDriverWait(driver, 5).until(
            expected_conditions.presence_of_element_located(
                (By.CLASS_NAME, 'nav-flyout')))
    except TimeoutException:
        assert False, 'Navigation flyout not visible within 5 seconds'
    else:
        links = driver.find_elements_by_class_name('nav-flyout__link')
        assert ('http://studiengaenge.zeit.de/sit'
                in links[0].get_attribute('href'))
        assert ('http://studiengaenge.zeit.de'
                in links[1].get_attribute('href'))
        assert ('https://ranking.zeit.de/che/de/'
                in links[2].get_attribute('href'))


def test_breadcrumbs_for_homepage(dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/index')
    view = zeit.web.campus.view_centerpage.Centerpage(context, dummy_request)

    assert view.breadcrumbs == []


def test_breadcrumbs_for_centerpage(dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/centerpage/index')
    view = zeit.web.campus.view_centerpage.Centerpage(context, dummy_request)

    breadcrumbs = [
        ('ZEIT Campus', 'http://xml.zeit.de/campus/index')
    ]

    assert view.breadcrumbs == breadcrumbs


def test_breadcrumbs_for_topicpage(dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/centerpage/thema')
    view = zeit.web.campus.view_centerpage.Centerpage(context, dummy_request)

    breadcrumbs = [
        ('ZEIT Campus', 'http://xml.zeit.de/campus/index'),
        (u'Thema: Jurastudium', None)
    ]

    assert view.breadcrumbs == breadcrumbs


def test_centerpage_contains_webtrekk_parameter_asset(testbrowser):
    browser = testbrowser('/campus/centerpage/cardstack')
    script = browser.cssselect(
        'script[src*="/static/js/webtrekk/webtrekk"] + script')[0]

    assert '27: "cardstack.1.2.1"' in script.text_content().strip()


def test_teaser_topic_link_title_should_match_kicker_and_headline(testbrowser):
    browser = testbrowser('/campus/centerpage/teaser-topic-variant')
    media_link_title = browser.cssselect(
        '.teaser-topic-variant__media-container a')[0].get('title')
    combined_link_title = browser.cssselect(
        '.teaser-topic-wide__combined-link')[0].get('title')
    assert media_link_title == combined_link_title


def test_cardstack_teaser_produces_correct_html(testbrowser):
    browser = testbrowser('/campus/centerpage/cardstack')
    teaser = browser.cssselect('.cp-cardstack')
    assert len(teaser) == 1
