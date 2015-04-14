# -*- coding: utf-8 -*-
import datetime
import re

import requests
import lxml
import mock
import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC  # NOQA
from selenium.common.exceptions import TimeoutException

import zeit.web.site.view_centerpage


screen_sizes = ((320, 480, True), (520, 960, True),
                (768, 1024, False), (980, 1024, False))


@pytest.fixture(scope='session', params=screen_sizes)
def screen_size(request):
    return request.param


def test_area_main_should_filter_teasers(application):
    context = mock.MagicMock()

    def create_mocked_teaserblocks():
        tb_large = mock.MagicMock()
        tb_large.layout.id = 'zon-large'
        tb_large.__len__.return_value = 2
        tb_large.__iter__ = lambda _: iter(['article'])

        tb_small = mock.MagicMock()
        tb_small.layout.id = 'zon-small'
        tb_small.__len__.return_value = 2
        tb_small.__iter__ = lambda _: iter(['article'])

        tb_no_layout = mock.MagicMock()
        tb_no_layout.layout = None
        tb_no_layout.__len__.return_value = 2

        tb_no_layout_id = mock.MagicMock()
        tb_no_layout_id.layout.id = None
        tb_no_layout_id.__len__.return_value = 2

        tb_no_teaser_in_block = mock.MagicMock()
        tb_no_teaser_in_block.layout.id = 'zon-small'
        tb_no_teaser_in_block.__iter__ = lambda _: iter([])

        return [tb_large, tb_small, tb_no_layout, tb_no_layout_id,
                tb_no_teaser_in_block]

    def val():
        m = mock.Mock()
        m.itervalues = create_mocked_teaserblocks().__iter__
        return [{'lead': m}]
    context.values = val

    request = mock.Mock()
    cp = zeit.web.site.view_centerpage.Centerpage(context, request)

    assert len(cp.area_main) == 2
    assert cp.area_main.values()[0].layout.id == 'zon-large'
    assert cp.area_main.values()[1].layout.id == 'zon-small'
    assert list(cp.area_main.values()[0])[0] == 'article'


def test_default_teaser_should_have_certain_blocks(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/teaser/default.tpl')

    assert 'teaser' in tpl.blocks, 'No block named teaser'
    assert 'teaser_modifier' in tpl.blocks, 'No teaser_modifier block'
    assert 'teaser_media_position_before_title' in tpl.blocks, (
        'No block named teaser_media_position_before_title')
    assert 'teaser_link' in tpl.blocks, 'No teaser_link block'
    assert 'teaser_media_position_after_title' in tpl.blocks, (
        'No block named teaser_media_position_after_title')
    assert 'teaser_container' in tpl.blocks, (
        'No block named teaser_container')
    assert 'teaser_text' in tpl.blocks, (
        'No block named teaser_text')
    assert 'teaser_byline' in tpl.blocks, (
        'No block named teaser_byline')
    assert 'teaser_metadata_default' in tpl.blocks, (
        'No block named teaser_metadata')
    assert 'teaser_datetime' in tpl.blocks, (
        'No block named teaser_datetime')
    assert 'teaser_commentcount' in tpl.blocks, (
        'No block named teaser_commentcount')


def test_default_teaser_should_match_css_selectors(application, jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/teaser/default.tpl')

    uid = 'http://xml.zeit.de/artikel/01'
    teaser = zeit.cms.interfaces.ICMSContent(uid)
    teaser.teaserSupertitle = 'teaserSupertitle'
    teaser.teaserTitle = 'teaserTitle'
    teaser.teaserText = 'teaserText'
    view = {'comment_counts': {uid: 129}}

    html_str = tpl.render(teaser=teaser, layout='teaser', view=view)
    html = lxml.html.fromstring(html_str).cssselect

    assert len(html('article.teaser h2.teaser__heading')) == 1, (
        'No headline is present')

    link = html('a.teaser__combined-link')[0]
    assert link.attrib['href'] == uid, 'No link is present'
    assert link.attrib['title'] == 'teaserSupertitle - teaserTitle', (
        'There is no link title')

    link_kicker = html('a.teaser__combined-link span.teaser__kicker')[0]
    assert link_kicker.text == 'teaserSupertitle', 'A kicker is missing'

    link_title = html('a.teaser__combined-link span.teaser__title')[0]
    assert link_title.text == 'teaserTitle', 'A teaser title is missing'

    assert len(html('article > div.teaser__container')) == 1, (
        'No teaser container')

    teaser_text = html('div.teaser__container > p.teaser__text')[0]
    assert teaser_text.text == 'teaserText', 'No teaser text'

    teaser_byline = html('div.teaser__container > span.teaser__byline')[0]
    assert teaser_byline.text == 'Von Anne Mustermann', (
        'No byline present')

    assert len(html('div.teaser__container > div.teaser__metadata')) == 1, (
        'No teaser metadata container')
    teaser_datetime = html('div.teaser__metadata > time.teaser__datetime')[0]
    assert teaser_datetime.text is None, 'Outdated datetime present'

    assert teaser_datetime.attrib['datetime'] == '2013-10-08T09:25:03+00:00', (
        'Incorrect datetime attribute')

    teaser_co = html('div.teaser__metadata > a.teaser__commentcount')[0]

    assert teaser_co.attrib['href'] == teaser.uniqueId + '#comments', (
        'No comment link href present')

    assert teaser_co.attrib['title'] == '129 Kommentare', (
        'No comment link title present')

    assert teaser_co.text == '129 Kommentare', (
        'No comment text present')


def test_first_small_teaser_has_no_image_on_mobile_mode(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.set_window_size(320, 480)
    driver.get('%s/zeit-online/fullwidth-onimage-teaser' % testserver.url)
    box = driver.find_elements_by_class_name('cp-area--lead')[0]
    first = box.find_elements_by_class_name('teaser-small__media')[0]
    second = box.find_elements_by_class_name('teaser-small__media')[1]

    assert first.is_displayed() is False, 'image is displayed'
    assert second.is_displayed() is False, 'image is displayed'


def test_fullwidth_teaser_should_be_rendered(testserver, testbrowser):
    browser = testbrowser('%s/zeit-online/fullwidth-teaser' % testserver.url)

    teaser_box = browser.cssselect('.cp-area.cp-area--fullwidth')
    teaser = browser.cssselect('.teaser-fullwidth')

    assert len(teaser_box) == 1, 'No fullwidth teaser box'
    assert len(teaser) == 1, 'No fullwidth teaser'


def test_fullwidth_teaser_has_correct_width_in_all_screen_sizes(
        selenium_driver, testserver, screen_size):
    driver = selenium_driver
    driver.set_window_size(screen_size[0], screen_size[1])
    driver.get('%s/zeit-online/fullwidth-teaser' % testserver.url)
    teaser = driver.find_elements_by_class_name('teaser-fullwidth')[0]
    helper = driver.find_elements_by_class_name(
        'teaser-fullwidth__inner-helper')[0]

    assert teaser.is_displayed(), 'Fullwidth teaser missing'
    assert helper.is_displayed(), 'Fullwidth teaser helper missing'

    if screen_size[0] == 768:
        # test ipad width
        assert helper.size.get('width') == 574
    elif screen_size[0] == 980:
        assert helper.size.get('width') == 640


def test_main_teasers_should_be_rendered_correctly(testserver, testbrowser):
    browser = testbrowser(
        '%s/zeit-online/main-teaser-setup' % testserver.url)

    articles = browser.cssselect('#main .cp-region .cp-area--lead article')
    assert len(articles) == 3, 'We expect 3 articles here'


def test_main_teasers_should_have_ids_attached(testserver, testbrowser):
    browser = testbrowser(
        '%s/zeit-online/main-teaser-setup' % testserver.url)

    all_articles = len(browser.cssselect('.teaser'))
    articles_with_ids = len(browser.cssselect('.teaser[data-unique-id]'))
    assert all_articles == articles_with_ids, 'We expect all teasers here'


def test_main_teasers_should_have_id_attached(testserver, testbrowser):
    browser = testbrowser(
        '%s/zeit-online/main-teaser-setup' % testserver.url)

    body = browser.cssselect(
        'body[data-unique-id="'
        'http://xml.zeit.de/zeit-online/main-teaser-setup"]')
    assert len(body) == 1, 'Body element misses data-attribute unique-id'


def test_main_teasers_should_have_type_attached(testserver, testbrowser):
    browser = testbrowser(
        '%s/zeit-online/main-teaser-setup' % testserver.url)

    body = browser.cssselect(
        'body[data-page-type="centerpage"]')
    assert len(body) == 1, 'Body element misses data-attribute page-type'


def test_responsive_image_should_render_correctly(testserver, testbrowser):
    browser = testbrowser(
        '%s/zeit-online/main-teaser-setup' % testserver.url)

    image = browser.cssselect(
        '#main .cp-region .cp-area'
        ' article:first-of-type figure.scaled-image'
        ' a > img')
    assert len(image) == 1, 'Only one image for first article'


def test_image_should_be_on_position_b(testserver, testbrowser):
    browser = testbrowser(
        '%s/zeit-online/main-teaser-setup' % testserver.url)
    articles = browser.cssselect('#main .cp-region .cp-area article')

    assert articles[0][0][1].tag == 'figure', 'This position should haz image'


def test_image_should_be_on_position_a(testserver, testbrowser):
    browser = testbrowser(
        '%s/zeit-online/main-teaser-setup' % testserver.url)
    articles = browser.cssselect('#main .cp-region .cp-area article')

    assert articles[1][0].tag == 'figure', 'An img should be on this position'


def test_responsive_image_should_have_noscript(testserver, testbrowser):
    browser = testbrowser(
        '%s/zeit-online/main-teaser-setup' % testserver.url)

    noscript = browser.cssselect(
        '#main .cp-region--lead .cp-area article figure noscript')
    assert len(noscript) == 2, 'No noscript areas found'


def test_topiclinks_title_schould_have_a_value_and_default_value():
    mycp = mock.Mock()
    mycp.topiclink_title = 'My Title'
    view = zeit.web.site.view_centerpage.Centerpage(mycp, mock.Mock())

    assert view.topiclink_title == 'My Title', 'There is no title present'

    mycp = mock.Mock()
    mycp.topiclink_title = None
    view = zeit.web.site.view_centerpage.Centerpage(mycp, mock.Mock())

    assert view.topiclink_title == 'Schwerpunkte', 'There is no title present'


def test_centerpage_view_should_have_topic_links():

    mycp = mock.Mock()

    mycp.topiclink_title = 'My Title'
    mycp.topiclink_label_1 = 'Label 1'
    mycp.topiclink_url_1 = 'http://link_1'
    mycp.topiclink_label_2 = 'Label 2'
    mycp.topiclink_url_2 = 'http://link_2'
    mycp.topiclink_label_3 = 'Label 3'
    mycp.topiclink_url_3 = 'http://link_3'

    topiclinks = list(zeit.web.core.centerpage.TopicLink(mycp))

    assert topiclinks == [('Label 1', 'http://link_1'),
                          ('Label 2', 'http://link_2'),
                          ('Label 3', 'http://link_3')]


def test_cp_areas_should_be_rendered_correctly(testserver, testbrowser):
    browser = testbrowser(
        '%s/zeit-online/fullwidth-onimage-teaser' % testserver.url)

    fullwidth = browser.cssselect('.cp-area.cp-area--fullwidth')
    content = browser.cssselect('.cp-area.cp-area--twothirds.cp-area--lead')
    informatives = browser.cssselect(
        '.cp-area.cp-area--onethird.cp-area--informatives')

    assert len(fullwidth) == 1, 'We expect 1 div here'
    assert len(content) == 1, 'We expect 1 div here'
    assert len(informatives) == 1, 'We expect 1 div here'


def test_column_teaser_should_render_series_element(testserver, testbrowser):

    browser = testbrowser(
        '%s/zeit-online/teaser-types-setup' % testserver.url)

    col_element = browser.cssselect(
        '.teaser-column .teaser-column__series')
    assert len(col_element) == 1
    assert col_element[0].text == u'F\xfcnf vor acht'


def test_column_teaser_should_have_mobile_layout(
        selenium_driver, testserver, screen_size):

    driver = selenium_driver
    driver.set_window_size(screen_size[0], screen_size[1])
    driver.get('%s/zeit-online/teaser-types-setup' % testserver.url)
    img_box = driver.find_elements_by_class_name('teaser-column__media')[0]
    assert img_box.is_displayed(), 'image box is not displayed'

    width_script = 'return $(".teaser-column__media").width()'
    width = driver.execute_script(width_script)

    if screen_size[0] == 320:
        assert width == 80, 'mobile: imgage box of wrong size'
    elif screen_size[0] == 520:
        assert width == 80, 'phablet: imgage box of wrong size'
    elif screen_size[0] == 768:
        assert width == 80, 'ipad: imgage box of wrong size'
    else:
        assert width > 200, 'desktop: image box of wrong size'


def test_column_teaser_should_have_different_font(
        selenium_driver, testserver, screen_size):

    driver = selenium_driver
    driver.get('%s/zeit-online/teaser-types-setup' % testserver.url)

    font_script = 'return $(".teaser-column__title").css("font-family")'
    font = driver.execute_script(font_script)
    assert "TabletGothic" in font, 'teaser column font is wrong'


def test_series_teaser_should_render_series_element(testserver, testbrowser):

    browser = testbrowser(
        '%s/zeit-online/teaser-serie-setup' % testserver.url)

    series_element = browser.cssselect('.teaser-series__label')
    assert len(series_element) == 2
    assert series_element[0].text == 'Serie: App-Kritik'


def test_series_teaser_should_have_mobile_layout(
        selenium_driver, testserver, screen_size):

    driver = selenium_driver
    driver.set_window_size(screen_size[0], screen_size[1])
    driver.get('%s/zeit-online/teaser-serie-setup' % testserver.url)
    img_box = driver.find_elements_by_class_name('teaser-series__media')[0]
    assert img_box.is_displayed(), 'image box is not displayed'

    width_script = 'return $(".teaser-series__media").width()'
    width = driver.execute_script(width_script)

    border_script = 'return $(".teaser-series").css("border-top-style")'
    border = driver.execute_script(border_script)

    if screen_size[0] == 320:
        assert width > 250  # mobile: imgage box of wrong size
        assert border == 'solid'  # mobile: border-top wrong
    elif screen_size[0] == 520:
        assert width == 150  # phablet: imgage box of wrong size
        assert border == 'dotted'  # phablet: border-top wrong
    elif screen_size[0] == 768:
        assert width == 150  # ipad: imgage box of wrong size
        assert border == 'dotted'  # ipad: border-top wrong
    else:
        assert width == 250  # desktop: image box of wrong size
        assert border == 'dotted'  # desktop: border-top wrong


def test_snapshot_displayed_after_scroll(
        selenium_driver, testserver, screen_size):
    driver = selenium_driver
    driver.set_window_size(screen_size[0], screen_size[1])
    driver.get('%s/zeit-online/index' % testserver.url)
    driver.execute_script(
        "window.scrollTo(0, $('.footer').get(0).offsetTop);")
    try:
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, 'snapshot')))
    except TimeoutException:
        assert False, 'Snapshot not visible after scrolled into view'


def test_snapshot_displayed_after_direct_load_with_anchor(
        selenium_driver, testserver, screen_size):
    driver = selenium_driver
    driver.set_window_size(screen_size[0], screen_size[1])
    driver.get('%s/zeit-online/index#snapshot' % testserver.url)
    try:
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, 'snapshot')))
    except TimeoutException:
        assert False, 'Snapshot not visible after scrolled into view'


def test_snapshot_morelink_text_icon_switch(
        selenium_driver, testserver, screen_size):
    driver = selenium_driver
    driver.set_window_size(screen_size[0], screen_size[1])
    driver.get('%s/zeit-online/index' % testserver.url)
    driver.execute_script(
        "window.scrollTo(0, $('.footer').get(0).offsetTop);")
    if screen_size[0] == 320:
        linkdisplay = driver.execute_script(
            'return $(".snapshot-readmore__item").css("display")')
        assert linkdisplay == u'none', 'Linktext not hidden on mobile'
    else:
        linkdisplay = driver.execute_script(
            'return $(".snapshot-readmore__item").css("display")')
        assert linkdisplay == u'inline', 'Linktext hidden on other than mobile'


def test_snapshot_should_display_copyright_with_nonbreaking_space(
        testserver, testbrowser):

    browser = testbrowser('%s/zeit-online/index' % testserver.url)

    copyright = browser.cssselect('.snapshot-caption__item')

    assert u'\xa9\xa0' in copyright[0].text, (
        'Copyright text hast no copyright sign with non breaking space')


def test_snapshot_should_not_be_displayed_where_no_snapshot_is_present(
        testserver, testbrowser):

    browser = testbrowser(
        '%s/zeit-online/main-teaser-setup' % testserver.url)

    assert not browser.cssselect('#snapshot'), (
        'There is an snaphot on a page which should not have one')


def test_snapshot_should_have_description_text(testserver, testbrowser):

    browser = testbrowser('%s/zeit-online/index' % testserver.url)
    description = browser.cssselect('.snapshot-caption')
    text = u'Die Installation "Cantareira-Wüste" des brasilianischen Künstlers'
    assert text in description[0].text


def test_small_teaser_without_image_has_no_padding_left(
        selenium_driver, testserver):

    driver = selenium_driver
    driver.set_window_size(768, 600)
    driver.get('%s/zeit-online/teaser-serie-setup' % testserver.url)
    teaser = driver.find_element_by_css_selector(
        '*[data-unique-id*="/article-ohne-bild"] .teaser-small__container')
    assert teaser.location.get('x') is 20


def test_parquet_region_list_should_have_regions(application):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/parquet-teaser-setup')
    view = zeit.web.site.view_centerpage.LegacyCenterpage(cp, mock.Mock())
    assert len(view.region_list_parquet) == 4, (
        'View contains {} parquet regions instead of 4' % len(
            view.region_list_parquet))


def test_parquet_regions_should_have_one_area_each(application):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/parquet-teaser-setup')
    view = zeit.web.site.view_centerpage.LegacyCenterpage(cp, mock.Mock())
    assert all([len(region) == 1 for region in view.region_list_parquet])


def test_parquet_region_areas_should_have_multiple_modules_each(application):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/parquet-teaser-setup')
    view = zeit.web.site.view_centerpage.LegacyCenterpage(cp, mock.Mock())
    assert all([len(area.values()) > 1 for region in view.region_list_parquet
                for area in region.values()])


def test_parquet_should_render_desired_amount_of_teasers(
        testbrowser, testserver):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/parquet-teaser-setup')
    view = zeit.web.site.view_centerpage.Centerpage(cp, mock.Mock())
    desired_amount = view.context.values()[1][0][0].display_amount
    browser = testbrowser(
        '%s/zeit-online/parquet-teaser-setup' % testserver.url)
    teasers = browser.cssselect(
        '#parquet > .parquet-row:first-child '
        'article[data-block-type="teaser"]')
    actual_amount = len(teasers)
    assert actual_amount == desired_amount, (
        'Parquet row does not display the right amount of teasers.'
        'Got %s, expected %s.' % (actual_amount, desired_amount))


def test_parquet_should_display_meta_links_only_on_desktop(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-online/parquet-teaser-setup' % testserver.url)

    topic_links = driver.find_element_by_css_selector(
        '.parquet-meta__topic-links')
    more_link = driver.find_element_by_css_selector(
        '.parquet-meta__more-link')

    driver.set_window_size(520, 960)
    assert not topic_links.is_displayed(), (
        'Parquet topic-links should not be displayed on mobile.')
    assert not more_link.is_displayed(), (
        'Parquet more-link should not be displayed on mobile.')

    driver.set_window_size(980, 1024)
    assert topic_links.is_displayed(), (
        'Parquet topic-links must be displayed on desktop.')
    assert more_link.is_displayed(), (
        'Parquet more-link must be displayed on desktop.')


def test_parquet_teaser_small_should_show_no_image_on_mobile(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-online/parquet-teaser-setup' % testserver.url)
    small_teaser = driver.find_element_by_css_selector(
        '.teaser-parquet-small__media')

    driver.set_window_size(320, 480)
    assert not small_teaser.is_displayed(), (
        'Small parquet teaser should hide it‘s image on mobile.')

    driver.set_window_size(980, 1024)
    assert small_teaser.is_displayed(), (
        'Small parquet teaser must show it‘s image on desktop.')


def test_video_series_should_be_available(application):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/index')
    view = zeit.web.site.view_centerpage.Centerpage(cp, mock.Mock())
    video_series = view.video_series_list
    assert len(video_series) > 0, (
        'Series object is empty')


def test_videostage_should_have_right_video_count(testserver, testbrowser):
    browser = testbrowser('%s/zeit-online/index' % testserver.url)

    videos = browser.cssselect('#video-stage article')
    assert len(videos) == 4, 'We expect 4 videos in video-stage'


def test_videos_should_have_video_ids(testserver, testbrowser):
    browser = testbrowser('%s/zeit-online/index' % testserver.url)

    videos = browser.cssselect('#video-stage article')
    for video in videos:
        attr = video.attrib
        videoid = attr.get('data-video-id')
        assert videoid is not ''


def test_series_select_should_navigate_away(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-online/index' % testserver.url)
    select = driver.find_element_by_css_selector('#series_select')
    for option in select.find_elements_by_tag_name('option'):
        if option.text == 'Rekorder':
            option.click()
            break
    driver.implicitly_wait(10)  # seconds
    assert '/serie/rekorder' in driver.current_url


def test_video_stage_video_should_play(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-online/index' % testserver.url)
    article = driver.find_element_by_css_selector(
        '#video-stage .video-large')
    videolink = driver.find_element_by_css_selector(
        '#video-stage .video-large figure')
    videolink.click()
    try:
        player = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '#video-stage .video-player__iframe'))
        )
        assert article.get_attribute(
            'data-video-id') in player.get_attribute('src')
    except TimeoutException:
        assert False, 'Video not visible with 10 seconds'


def test_module_printbox_should_contain_teaser_image(testserver):
    mycp = mock.Mock()
    view = zeit.web.site.view_centerpage.LegacyCenterpage(mycp, mock.Mock())
    image = view.module_printbox[0].image
    assert isinstance(image, zeit.content.image.image.RepositoryImage)


def test_homepage_indentifies_itself_as_homepage(testserver):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/index')
    view = zeit.web.site.view_centerpage.Centerpage(cp, mock.Mock())
    assert view.is_hp is True
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/main-teaser-setup')
    view = zeit.web.site.view_centerpage.Centerpage(cp, mock.Mock())
    assert view.is_hp is False


def test_homepage_ressort_is_homepage(testserver):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/index')
    view = zeit.web.site.view_centerpage.Centerpage(cp, mock.Mock())
    assert view.ressort == 'homepage'


def test_linkobject_teaser_should_contain_supertitle(testserver, testbrowser):
    browser = testbrowser('%s/zeit-online/index' % testserver.url)
    uid = 'http://xml.zeit.de/zeit-online/cp-content/link_teaser'
    kicker = browser.cssselect('.teaser-small[data-unique-id="{}"] '
                               '.teaser-small__kicker'.format(uid))[0]
    assert kicker.text == 'Freier Teaser Kicker'


def test_blog_teaser_should_have_specified_markup(testserver, testbrowser):
    browser = testbrowser('%s/zeit-online/index' % testserver.url)
    uid = 'http://xml.zeit.de/blogs/nsu-blog-bouffier'
    kicker = browser.cssselect('.teaser-blog[data-unique-id="{}"] '
                               '.teaser-blog__kicker'.format(uid))[0]
    assert kicker.text == 'Zeugenvernehmung'

    marker = browser.cssselect('.teaser-blog[data-unique-id="{}"] '
                               '.teaser-blog__marker'.format(uid))[0]
    assert marker.text == 'Blog'

    name_of_blog = browser.cssselect('.teaser-blog[data-unique-id="{}"] '
                                     '.teaser-blog__name'.format(uid))[0]
    assert re.sub(r'^\s+|\t|\n|\s+$', '', name_of_blog.text) == 'NSU-Prozess /'

    title = browser.cssselect('.teaser-blog[data-unique-id="{}"] '
                              '.teaser-blog__title'.format(uid))[0]
    assert title.text == 'Beate, die harmlose Hausfrau'

    blog_text = browser.cssselect('.teaser-blog[data-unique-id="{}"] '
                                  '.teaser-blog__text'.format(uid))[0]
    assert 'Lorem ipsum' in blog_text.text

    byline = browser.cssselect('.teaser-blog[data-unique-id="{}"] '
                               '.teaser-blog__byline'.format(uid))[0]
    assert byline.text == 'Von Anne Mustermann'


def test_gallery_teaser_should_contain_supertitle(testserver, testbrowser):
    browser = testbrowser('%s/zeit-online/index' % testserver.url)
    uid = 'http://xml.zeit.de/galerien/fs-desktop-schreibtisch-computer'
    kicker = browser.cssselect('.teaser-small[data-unique-id="{}"] '
                               '.teaser-small__kicker'.format(uid))[0]
    assert kicker.text == 'Desktop-Bilder'


def test_oldads_toggle_is_off(application):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/index')
    view = zeit.web.site.view_centerpage.Centerpage(cp, mock.Mock())
    assert view.deliver_ads_oldschoolish is False


def test_centerpage_header_tags(application, jinja2_env):
    tpl = jinja2_env.get_template('zeit.web.site:templates/centerpage.html')
    view, request = (mock.Mock(),) * 2
    view.resolve = mock.Mock(return_value=request)
    view.topiclinks = [('Label 1', 'http://link_1'),
                       ('Label 2', 'http://link_2'),
                       ('Label 3', 'http://link_3')]
    view.topiclink_title = 'My Title'
    view.displayed_last_published_semantic = datetime.datetime.now()

    html_str = ' '.join(list(tpl.blocks['metadata'](view)))
    html = lxml.html.fromstring(html_str).cssselect
    tags = html('.header__tags__link')

    assert len(html('.header__tags')) == 1, 'just one .header__tags'
    assert html('.header__tags__label')[0].text == 'My Title'
    assert len(tags) == 3
    assert tags[0].get('href') == 'http://link_1'
    assert tags[0].get('title') == 'Label 1'
    assert tags[0].text == 'Label 1'


def test_centerpage_metadata(testbrowser, testserver):
    browser = testbrowser('%s/zeit-online/index' % testserver.url)
    html_str = browser.contents
    html = lxml.html.fromstring(html_str).cssselect
    date = '3. Dezember 2014, 12:50 Uhr'

    assert len(html('.header__tags')) == 1, 'just one .header__tags'
    assert html('.header__tags__label')[0].text == 'Schwerpunkte'

    assert len(html('.header__date')) == 1, 'just one .header__date'
    assert html('.header__date')[0].text == date, 'Date is invalid'


def test_new_centerpage_renders(testserver):
    resp = requests.get('%s/index' % testserver.url)
    assert resp.ok
