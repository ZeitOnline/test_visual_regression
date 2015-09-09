# -*- coding: utf-8 -*-
import re

import lxml.html
import lxml.etree
import mock
import pytest
import requests

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

import zeit.content.cp.centerpage

import zeit.web.core.centerpage
import zeit.web.core.interfaces
import zeit.web.core.utils
import zeit.web.site.module.playlist
import zeit.web.site.view_centerpage


screen_sizes = ((320, 480, True), (520, 960, True),
                (768, 1024, False), (980, 1024, False))


@pytest.fixture(scope='session', params=screen_sizes)
def screen_size(request):
    return request.param


def test_area_major_should_correctly_process_teasers(application):
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
    context.ressort = 'ressort'

    request = mock.Mock()
    cp = zeit.web.site.view_centerpage.LegacyCenterpage(context, request)

    assert len(cp.area_major) == 4
    assert cp.area_major.values()[0].layout.id == 'zon-large'
    assert cp.area_major.values()[1].layout.id == 'zon-small'
    assert list(cp.area_major.values()[0])[0] == 'article'


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


def test_default_teaser_should_match_css_selectors(
        application, jinja2_env, testserver):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/teaser/default.tpl')

    teaser = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    cp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/centerpage/index')
    teaser.teaserSupertitle = 'teaserSupertitle'
    teaser.teaserTitle = 'teaserTitle'
    teaser.teaserText = 'teaserText'
    view = mock.Mock()
    view.comment_counts = {'http://xml.zeit.de/artikel/01': 129}
    view.context = cp
    view.request.route_url.return_value = '/'

    area = mock.Mock()
    area.kind = 'solo'

    module = mock.Mock()

    html_str = tpl.render(
        teaser=teaser, layout='teaser', view=view, area=area, module=module)
    html = lxml.html.fromstring(html_str).cssselect

    assert len(html('article.teaser h2.teaser__heading')) == 1

    link = html('a.teaser__combined-link')[0]
    assert link.attrib['href'] == '/artikel/01'
    assert link.attrib['title'] == 'teaserSupertitle - teaserTitle'

    link_kicker = html('a.teaser__combined-link span.teaser__kicker')[0]
    assert link_kicker.text == 'teaserSupertitle'

    link_title = html('a.teaser__combined-link span.teaser__title')[0]
    assert link_title.text == 'teaserTitle'

    assert len(html('article > div.teaser__container')) == 1

    teaser_text = html('div.teaser__container > p.teaser__text')[0]
    assert teaser_text.text == 'teaserText'

    assert len(html('div.teaser__container > div.teaser__metadata')) == 1
    byline = html('div.teaser__metadata > span.teaser__byline')[0]
    assert re.sub('\s+', ' ', byline.text).strip() == 'Von Anne Mustermann'

    teaser_co = html('div.teaser__metadata > a.teaser__commentcount')[0]

    assert teaser_co.attrib['href'] == teaser.uniqueId.replace(
        'http://xml.zeit.de', '') + '#comments'
    assert teaser_co.attrib['title'] == 'Kommentare anzeigen'
    assert teaser_co.text == '129 Kommentare'


def test_small_teaser_should_display_no_image_on_mobile(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.set_window_size(320, 480)
    driver.get('%s/zeit-online/slenderized-index' % testserver.url)
    box = driver.find_elements_by_class_name('cp-area--major')[0]
    teaser_image = box.find_elements_by_class_name('teaser-small__media')[0]

    assert teaser_image.is_displayed() is False, 'image is not displayed'


def test_fullwidth_teaser_should_be_rendered(testserver, testbrowser):
    browser = testbrowser('/zeit-online/fullwidth-teaser')
    teaser = browser.cssselect('.cp-area.cp-area--solo .teaser-fullwidth')
    teaser_column = browser.cssselect(
        '.cp-area.cp-area--solo .teaser-fullwidth-column')

    assert len(teaser) == 4
    assert len(teaser_column) == 1


def test_fullwidth_teaser_image_should_have_attributes_for_mobile_variant(
        testserver, testbrowser):
    browser = testbrowser('/zeit-online/fullwidth-teaser')
    img = browser.cssselect('.teaser-fullwidth__media-item')[0]
    assert img.attrib['data-mobile-variant'] == 'wide'
    assert img.attrib['data-mobile-ratio'].startswith('1.77')
    assert 'cp-content/ig-1/wide' in img.attrib['data-mobile-src']


def test_fullwidth_teaser_image_should_use_mobile_variant_on_mobile(
        selenium_driver, testserver):
    driver = selenium_driver

    driver.set_window_size(screen_sizes[1][0], screen_sizes[1][1])
    driver.get('%s/zeit-online/fullwidth-teaser' % testserver.url)
    img = driver.find_element_by_class_name('teaser-fullwidth__media-item')
    ratio = float(img.size['width']) / img.size['height']
    assert '/wide__' in img.get_attribute('src'), \
        'wide image variant should be used on mobile devices'
    assert 1.7 < ratio < 1.8, 'mobile ratio should be 16:9-ish'


def test_fullwidth_teaser_has_correct_width_in_all_screen_sizes(
        selenium_driver, testserver, screen_size):
    driver = selenium_driver
    driver.set_window_size(screen_size[0], screen_size[1])
    driver.get('%s/zeit-online/fullwidth-teaser' % testserver.url)
    teaser = driver.find_element_by_class_name('teaser-fullwidth')
    helper = driver.find_element_by_class_name('teaser-fullwidth__container')
    script = 'return document.documentElement.clientWidth'

    assert teaser.is_displayed(), 'Fullwidth teaser missing'
    assert helper.is_displayed(), 'Fullwidth teaser container missing'

    if screen_size[0] == 768:
        width = driver.execute_script(script)
        assert helper.size.get('width') == int('%.0f' % (width * 0.72))

    elif screen_size[0] == 980:
        width = driver.execute_script(script)
        assert helper.size.get('width') == int('%.0f' % (width * 0.6666))


def test_main_teasers_should_be_rendered_correctly(testserver, testbrowser):
    browser = testbrowser('/zeit-online/main-teaser-setup')

    articles = browser.cssselect('#main .cp-region .cp-area--major article')
    assert len(articles) == 3


def test_main_teasers_should_have_ids_attached(testserver, testbrowser):
    browser = testbrowser('/zeit-online/main-teaser-setup')

    all_articles = len(browser.cssselect('.teaser'))
    articles_with_ids = len(browser.cssselect('.teaser[data-unique-id]'))
    assert all_articles == articles_with_ids, 'We expect all teasers here'


def test_main_teasers_should_have_id_attached(testserver, testbrowser):
    browser = testbrowser('/zeit-online/main-teaser-setup')

    body = browser.cssselect(
        'body[data-unique-id="'
        'http://xml.zeit.de/zeit-online/main-teaser-setup"]')
    assert len(body) == 1, 'Body element misses data-attribute unique-id'


def test_main_teasers_should_have_type_attached(testserver, testbrowser):
    browser = testbrowser('/zeit-online/main-teaser-setup')

    body = browser.cssselect(
        'body[data-page-type="centerpage"]')
    assert len(body) == 1, 'Body element misses data-attribute page-type'


def test_responsive_image_should_render_correctly(testserver, testbrowser):
    browser = testbrowser('/zeit-online/main-teaser-setup')

    image = browser.cssselect(
        '#main .cp-region .cp-area'
        ' article:first-of-type figure.scaled-image'
        ' a > img')
    assert len(image) == 1, 'Only one image for first article'


def test_image_should_be_on_position_b(testserver, testbrowser):
    browser = testbrowser('/zeit-online/main-teaser-setup')
    articles = browser.cssselect('#main .cp-region .cp-area article')

    assert articles[0][0][1].tag == 'figure', 'This position should haz image'


def test_image_should_be_on_position_a(testserver, testbrowser):
    browser = testbrowser('/zeit-online/main-teaser-setup')
    articles = browser.cssselect('#main .cp-region .cp-area article')

    assert articles[1][0].tag == 'figure', 'An img should be on this position'


def test_responsive_image_should_have_noscript(testserver, testbrowser):
    browser = testbrowser('/zeit-online/main-teaser-setup')

    noscript = browser.cssselect(
        '#main .cp-region--multi .scaled-image noscript')
    assert len(noscript) == 3


def test_topic_links_title_schould_have_a_value_and_default_value(testserver):
    context = mock.Mock()
    context.topic_links = mock.Mock()
    context.topiclink_title = 'My Title'
    topic_links = zeit.web.core.centerpage.TopicLink(context)

    assert topic_links.title == 'My Title'

    context.topiclink_title = None
    topic_links = zeit.web.core.centerpage.TopicLink(context)

    assert topic_links.title == 'Schwerpunkte'


def test_centerpage_view_should_have_topic_links(testserver):
    mycp = mock.Mock()
    mycp.topiclink_label_1 = 'Label 1'
    mycp.topiclink_url_1 = 'http://link_1'
    mycp.topiclink_label_2 = 'Label 2'
    mycp.topiclink_url_2 = 'http://link_2'
    mycp.topiclink_label_3 = 'Label 3'
    mycp.topiclink_url_3 = 'http://link_3'

    topic_links = list(zeit.web.core.centerpage.TopicLink(mycp))

    assert topic_links == [('Label 1', 'http://link_1'),
                           ('Label 2', 'http://link_2'),
                           ('Label 3', 'http://link_3')]


def test_cp_areas_should_be_rendered_correctly(testserver, testbrowser):
    browser = testbrowser('/zeit-online/index')

    fullwidth = browser.cssselect('.cp-area.cp-area--solo .teaser-fullwidth')
    content = browser.cssselect('.cp-area.cp-area--major')
    informatives = browser.cssselect('.cp-area.cp-area--minor')

    assert len(fullwidth) == 1
    assert len(content) == 1
    assert len(informatives) == 1


def test_column_teaser_should_render_series_element(testserver, testbrowser):
    browser = testbrowser('/zeit-online/journalistic-formats')

    col_element = browser.cssselect(
        '.teaser-fullwidth-column__series-label')[0]
    assert col_element.text == u'Fünf vor acht'


def test_series_teaser_should_render_series_element(testserver, testbrowser):

    browser = testbrowser('/zeit-online/journalistic-formats')

    series_element = browser.cssselect('.teaser-large__series-label')
    assert series_element[0].text == 'Serie: App-Kritik'


def test_small_teaser_should_have_responsive_layout(
        selenium_driver, testserver, screen_size):

    driver = selenium_driver
    driver.set_window_size(screen_size[0], screen_size[1])
    driver.get('%s/zeit-online/slenderized-index' % testserver.url)

    width_script = 'return $(".teaser-small__media").first().width()'
    width = driver.execute_script(width_script)

    img_box = driver.find_elements_by_class_name('teaser-small__media')[0]

    if screen_size[0] == 320:
        assert not img_box.is_displayed(), 'no image should be shown on mobile'
    elif screen_size[0] == 520:
        assert width == 150
    elif screen_size[0] == 768:
        assert width == 150
    else:
        assert width == 250


def test_snapshot_hidden_on_initial_load(
        selenium_driver, testserver, screen_size):
    driver = selenium_driver
    driver.set_window_size(screen_size[0], screen_size[1])
    driver.get('%s/zeit-online/index' % testserver.url)
    snapshot = driver.find_element_by_id('snapshot')
    assert not snapshot.is_displayed(), 'Snapshot not hidden onload'


def test_snapshot_displayed_after_scroll(
        selenium_driver, testserver, screen_size):
    driver = selenium_driver
    driver.set_window_size(screen_size[0], screen_size[1])
    driver.get('%s/zeit-online/index' % testserver.url)
    driver.execute_script("window.scrollTo(0, \
        document.getElementById('snapshot').parentNode.offsetTop)")
    try:
        wait = WebDriverWait(driver, 10)
        wait.until(expected_conditions.visibility_of_element_located(
                   (By.ID, 'snapshot')))
    except TimeoutException:
        assert False, 'Snapshot not visible after scrolled into view'


def test_snapshot_displayed_after_direct_load_with_anchor(
        selenium_driver, testserver, screen_size):
    driver = selenium_driver
    driver.set_window_size(screen_size[0], screen_size[1])
    driver.get('%s/zeit-online/index#snapshot' % testserver.url)
    try:
        wait = WebDriverWait(driver, 10)
        wait.until(expected_conditions.visibility_of_element_located(
                   (By.ID, 'snapshot')))
    except TimeoutException:
        assert False, 'Snapshot not visible for link with fragment identifier'


def test_snapshot_morelink_text_icon_switch(
        selenium_driver, testserver, screen_size):
    driver = selenium_driver
    driver.set_window_size(screen_size[0], screen_size[1])
    driver.get('%s/zeit-online/index' % testserver.url)
    linkdisplay = driver.execute_script(
        "return $('#snapshot .section-heading__text').eq(0).css('display')")
    if screen_size[0] == 320:
        assert linkdisplay == u'none', 'Linktext not hidden on mobile'
    else:
        assert linkdisplay == u'inline', 'Linktext hidden on other than mobile'


def test_snapshot_should_display_copyright_with_nonbreaking_space(
        testserver, testbrowser):

    browser = testbrowser('/zeit-online/index')

    copyright = browser.cssselect('.snapshot-caption__item')

    assert u'\xa9\xa0' in copyright[0].text, (
        'Copyright text hast no copyright sign with non breaking space')


def test_snapshot_should_not_be_displayed_where_no_snapshot_is_present(
        testserver, testbrowser):

    browser = testbrowser('/zeit-online/main-teaser-setup')

    assert not browser.cssselect('#snapshot'), (
        'There is an snaphot on a page which should not have one')


def test_snapshot_should_have_description_text(testserver, testbrowser):

    browser = testbrowser('/zeit-online/index')
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
        'View contains %s parquet regions instead of 4' % len(
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
        '.cp-area--parquet .teaser-small__media')

    driver.set_window_size(320, 480)
    assert not small_teaser.is_displayed(), (
        'Small parquet teaser should hide it‘s image on mobile.')

    driver.set_window_size(980, 1024)
    assert small_teaser.is_displayed(), (
        'Small parquet teaser must show it‘s image on desktop.')


def test_playlist_video_series_should_be_available(application):
    playlist = zeit.web.site.module.playlist.Playlist(mock.Mock())
    assert len(playlist.video_series_list) == 24


def test_videostage_should_have_right_video_count(testserver, testbrowser):
    browser = testbrowser('/zeit-online/video-stage')
    videos = browser.cssselect('#video-stage article')
    assert len(videos) == 4, 'We expect 4 videos in video-stage'


def test_videostage_videos_should_have_video_ids(testserver, testbrowser):
    browser = testbrowser('/zeit-online/video-stage')
    videos = browser.cssselect('#video-stage article')
    for video in videos:
        attr = video.attrib
        videoid = attr.get('data-video-id')
        assert videoid is not ''


def test_videostage_series_select_should_navigate_away(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-online/video-stage' % testserver.url)
    select = driver.find_element_by_css_selector('#series_select')
    for option in select.find_elements_by_tag_name('option'):
        if option.text == 'Rekorder':
            option.click()
            break
    driver.implicitly_wait(10)  # seconds
    assert '/serie/rekorder' in driver.current_url


def test_videostage_video_should_play(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-online/video-stage' % testserver.url)
    article = driver.find_element_by_css_selector(
        '#video-stage .video-large')
    videolink = driver.find_element_by_css_selector(
        '#video-stage .video-large figure')
    videolink.click()
    try:
        player = WebDriverWait(driver, 10).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '#video-stage .video-player__iframe'))
        )
        assert article.get_attribute(
            'data-video-id') in player.get_attribute('src')
    except TimeoutException:
        assert False, 'Video not visible with 10 seconds'


def test_module_printbox_should_contain_teaser_image(application):
    mycp = mock.Mock()
    view = zeit.web.site.view_centerpage.LegacyCenterpage(mycp, mock.Mock())
    image = view.module_printbox.image
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
    browser = testbrowser('/zeit-online/index')
    uid = 'http://xml.zeit.de/zeit-online/cp-content/link_teaser'
    kicker = browser.cssselect('.teaser-small[data-unique-id="{}"] '
                               '.teaser-small__kicker'.format(uid))[0]
    assert kicker.text == 'Freier Teaser Kicker'


def test_blog_teaser_should_have_specified_markup(testserver, testbrowser):
    browser = testbrowser('/zeit-online/journalistic-formats')
    uid = 'http://xml.zeit.de/blogs/nsu-blog-bouffier'
    teaser = browser.cssselect(
        '.teaser-large[data-unique-id="{}"] '.format(uid))[0]

    kicker = teaser.cssselect('.teaser-large__kicker--blog')[0]
    assert kicker.text == 'Zeugenvernehmung'

    marker = teaser.cssselect('.blog-format__marker')[0]
    assert marker.text == 'Blog'

    name_of_blog = teaser.cssselect('.blog-format__name')[0]
    assert name_of_blog.text.strip() == 'NSU-Prozess'

    title = teaser.cssselect('.teaser-large__title')[0]
    assert title.text == 'Beate, die harmlose Hausfrau'

    blog_text = teaser.cssselect('.teaser-large__text')[0]
    assert 'Lorem ipsum' in blog_text.text

    byline = teaser.cssselect('.teaser-large__byline')[0]
    assert re.sub('\s+', ' ', byline.text).strip() == 'Von Anne Mustermann'


def test_gallery_teaser_should_contain_supertitle(testserver, testbrowser):
    browser = testbrowser('/zeit-online/index')
    uid = 'http://xml.zeit.de/galerien/fs-desktop-schreibtisch-computer'
    kicker = browser.cssselect('.teaser-small[data-unique-id="{}"] '
                               '.teaser-small__kicker'.format(uid))[0]
    assert kicker.text == 'Desktop-Bilder'


def test_centerpage_should_have_header_tags(testbrowser, testserver):
    browser = testbrowser('/zeit-online/index')
    html = lxml.html.fromstring(browser.contents).cssselect

    assert len(html('.header__tags')) == 1
    assert html('.header__tags__label')[0].text == 'Schwerpunkte'

    assert len(html('.header__tags__link')) == 3
    assert html('.header__tags__link')[0].get('href').endswith(
        '/schlagworte/organisationen/islamischer-staat/index')
    assert html('.header__tags__link')[0].text == 'Islamischer Staat'


def test_new_centerpage_renders(testserver):
    resp = requests.get('%s/zeit-online/slenderized-index' % testserver.url)
    assert resp.ok


def test_minor_teaser_has_correct_width_in_all_screen_sizes(
        selenium_driver, testserver, screen_size):
    driver = selenium_driver
    driver.set_window_size(screen_size[0], screen_size[1])
    driver.get('%s/zeit-online/slenderized-index' % testserver.url)
    teaser = driver.find_elements_by_class_name('teaser-small-minor')[0]
    main = driver.find_element_by_id('main')
    main_width = main.size.get('width')
    gutter_width = 20

    assert teaser.is_displayed(), 'Fullwidth teaser missing'

    if screen_size[0] == 320:
        assert teaser.size.get('width') == main_width
    elif screen_size[0] == 520:
        assert teaser.size.get('width') == main_width
    elif screen_size[0] == 768:
        assert teaser.size.get('width') == (int(
            round((main_width - gutter_width) / 3.0) - gutter_width))
    elif screen_size[0] == 980:
        assert teaser.size.get('width') == (int(
            round((main_width - gutter_width) / 3.0) - gutter_width))


def test_adcontroller_values_return_values_on_hp(application):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/index')
    adcv = [
        ('$handle', 'homepage'),
        ('level2', 'homepage'),
        ('level3', ''),
        ('level4', ''),
        ('$autoSizeFrames', True),
        ('keywords', 'zeitonline'),
        ('tma', '')]
    view = zeit.web.site.view_centerpage.LegacyCenterpage(cp, mock.Mock())
    assert adcv == view.adcontroller_values


def test_adcontroller_values_return_values_on_cp(application):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/main-teaser-setup')
    adcv = [
        ('$handle', 'index'),
        ('level2', 'politik'),
        ('level3', ''),
        ('level4', ''),
        ('$autoSizeFrames', True),
        ('keywords', 'zeitonline'),
        ('tma', '')]
    view = zeit.web.site.view_centerpage.LegacyCenterpage(cp, mock.Mock())
    assert adcv == view.adcontroller_values


def test_canonical_url_returns_correct_value_on_cp(application):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/index')
    request = mock.Mock()
    request.url = 'http://localhorst/centerpage/index'
    view = zeit.web.site.view_centerpage.LegacyCenterpage(cp, request)
    assert view.canonical_url == 'http://localhorst/centerpage/index'


def test_canonical_ruleset_on_diverse_pages(testserver, testbrowser):
    url = '%s/zeit-online/index' % testserver.url
    browser = testbrowser(url)
    link = browser.cssselect('link[rel="canonical"]')
    assert link[0].get('href') == url

    url = '%s/zeit-online/article/01' % testserver.url
    browser = testbrowser(url)
    link = browser.cssselect('link[rel="canonical"]')
    assert link[0].get('href') == url

    url = '%s/zeit-online/article/zeit' % testserver.url
    browser = testbrowser(url)
    link = browser.cssselect('link[rel="canonical"]')
    assert link[0].get('href') == url

    url = '%s/zeit-online/article/zeit' % testserver.url
    browser = testbrowser("{}/komplettansicht".format(url))
    link = browser.cssselect('link[rel="canonical"]')
    assert link[0].get('href') == url

    url = '%s/zeit-online/article/zeit' % testserver.url
    browser = testbrowser("{}/seite-2".format(url))
    link = browser.cssselect('link[rel="canonical"]')
    assert link[0].get('href') == url + '/seite-2'

    url = '%s/suche/index' % testserver.url
    browser = testbrowser(url)
    link = browser.cssselect('link[rel="canonical"]')
    assert link[0].get('href') == url

    url = '%s/suche/index' % testserver.url
    browser = testbrowser("{}?p=2".format(url))
    link = browser.cssselect('link[rel="canonical"]')
    assert link[0].get('href') == url + '?p=2'

    url = '%s/dynamic/ukraine' % testserver.url
    browser = testbrowser(url)
    link = browser.cssselect('link[rel="canonical"]')
    assert link[0].get('href') == url

    url = '%s/dynamic/ukraine' % testserver.url
    browser = testbrowser("{}?p=2".format(url))
    link = browser.cssselect('link[rel="canonical"]')
    assert link[0].get('href') == url + '?p=2'


def test_robots_rules_for_angebote_paths(application):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/index')
    request = mock.Mock()

    # usual angebot
    request.path = '/angebote/immobilien/test'
    view = zeit.web.site.view_centerpage.Centerpage(cp, request)
    assert view.meta_robots == 'index,nofollow,noodp,noydir,noarchive', (
        'wrong robots for usual angebot')

    # partnersuche
    request.path = '/angebote/partnersuche/test'
    view = zeit.web.site.view_centerpage.Centerpage(cp, request)
    assert view.meta_robots == 'index,follow,noodp,noydir,noarchive', (
        'wrong robots for partnersuche')


def test_robots_rules_for_diverse_paths(application):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/index')
    request = mock.Mock()
    request.url = 'http://localhost'

    # test folder
    request.path = '/test/'
    view = zeit.web.site.view_centerpage.Centerpage(cp, request)
    assert view.meta_robots == 'noindex,follow,noodp,noydir,noarchive', (
        'wrong robots for test folder')

    # templates folder
    request.path = '/templates/'
    view = zeit.web.site.view_centerpage.Centerpage(cp, request)
    assert view.meta_robots == 'noindex,follow,noodp,noydir,noarchive', (
        'wrong robots for templates folder')

    # banner folder
    request.path = '/banner/'
    view = zeit.web.site.view_centerpage.Centerpage(cp, request)
    assert view.meta_robots == 'noindex,follow,noodp,noydir,noarchive', (
        'wrong robots for banner folder')

    # any folder
    request.path = '/any/'
    view = zeit.web.site.view_centerpage.Centerpage(cp, request)
    assert view.meta_robots == 'index,follow,noodp,noydir,noarchive', (
        'wrong robots for any other folder')


def test_newsticker_should_have_expected_dom(testserver, testbrowser):
    browser = testbrowser('/zeit-online/news-teaser')

    cols = browser.cssselect('.cp-area--newsticker .newsticker__column')
    assert len(cols) == 2
    teaser = browser.cssselect('.cp-area--newsticker article.newsteaser')
    assert len(teaser) == 8
    assert len(teaser[0].cssselect('time')) == 1
    assert len(
        teaser[0].cssselect('.newsteaser__text a .newsteaser__kicker')) == 1
    assert len(
        teaser[0].cssselect('.newsteaser__text a .newsteaser__title')) == 1
    assert len(
        teaser[0].cssselect('.newsteaser__text .newsteaser__product')) == 1


def test_servicebox_present_in_wide_breakpoints(
        selenium_driver, testserver, screen_size):
    driver = selenium_driver
    driver.set_window_size(screen_size[0], screen_size[1])
    driver.get('%s/zeit-online/slenderized-index' % testserver.url)
    servicebox = driver.find_element_by_id('servicebox')

    if screen_size[0] == 320:
        assert servicebox.is_displayed() is False, 'Servicebox displayed'
    if screen_size[0] == 520:
        assert servicebox.is_displayed() is False, 'Servicebox displayed'
    if screen_size[0] == 768:
        assert servicebox.is_displayed() is True, 'Servicebox not displayed'
    if screen_size[0] == 980:
        assert servicebox.is_displayed() is True, 'Servicebox not displayed'


def test_centerpage_area_should_render_in_isolation(testbrowser, testserver):
    browser = testbrowser('/index/area/id-5fe59e73-e388-42a4-a8d4-'
                          '750b0bf96812')
    select = browser.cssselect
    assert len(select('div.cp-area.cp-area--gallery')) == 1
    assert len(select('article.teaser-gallery')) == 2


def test_centerpage_should_render_bam_style_buzzboxes(testbrowser, testserver):
    browser = testbrowser('/centerpage/zeitonline')
    assert browser.cssselect('.buzz-box')
    assert len(browser.cssselect('.buzz-box__teasers article')) == 3


def test_centerpage_square_teaser_has_pixelperfect_image(
        testbrowser, testserver):
    browser = testbrowser('/zeit-online/teaser-square-setup')
    images = browser.cssselect('.teaser-square .scaled-image')
    assert len(images)
    for image in images:
        assert 'is-pixelperfect' in image.get('class')


def test_centerpage_teaser_is_clickable_en_block_for_touch_devices(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-online/index?touch' % testserver.url)
    article = driver.find_element_by_css_selector('article[data-unique-id]')
    link = article.find_element_by_tag_name('a')
    href = link.get_attribute('href')
    article.click()
    assert driver.current_url == href

    driver.back()
    article = driver.find_element_by_css_selector('article[data-unique-id]')
    text = article.find_element_by_tag_name('p')
    text.click()
    assert driver.current_url == href


def test_gallery_teaser_exists(testbrowser, testserver):
    select = testbrowser('/zeit-online/teaser-gallery-setup').cssselect
    assert len(select('.cp-region--gallery')) == 1
    assert len(select('.cp-area--gallery')) == 1


def test_gallery_teaser_has_ressort_heading(testbrowser, testserver):
    select = testbrowser('/zeit-online/teaser-gallery-setup').cssselect
    title = select('.cp-area--gallery .section-heading__title')
    assert len(title) == 1
    assert "Fotostrecken" in title[0].text


def test_gallery_teaser_has_correct_elements(testbrowser, testserver):
    wanted = 2
    browser = testbrowser('/zeit-online/teaser-gallery-setup')
    area = browser.cssselect('.cp-area--gallery')[0]

    assert len(area.cssselect('.teaser-gallery')) == wanted
    assert len(area.cssselect('.teaser-gallery__figurewrapper')) == wanted
    assert len(area.cssselect('.teaser-gallery__media')) == wanted
    assert len(area.cssselect('.teaser-gallery__icon')) == wanted
    assert len(area.cssselect('.teaser-gallery__counter')) == wanted
    assert len(area.cssselect('.teaser-gallery__container')) == wanted
    assert len(area.cssselect('.teaser-gallery__heading')) == wanted
    assert len(area.cssselect('.teaser-gallery__kicker')) == wanted
    assert len(area.cssselect('.teaser-gallery__title')) == wanted
    assert len(area.cssselect('.teaser-gallery__text')) == wanted


def test_gallery_teaser_hides_elements_on_mobile(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('{}/zeit-online/teaser-gallery-setup'.format(testserver.url))

    ressort_linktext = driver.find_element_by_css_selector(
        '.section-heading__text')
    gallery_counter = driver.find_element_by_css_selector(
        '.teaser-gallery__counter')
    gallery_text = driver.find_element_by_css_selector(
        '.teaser-gallery__text')

    driver.set_window_size(480, 600)
    assert not ressort_linktext.is_displayed(), (
        'Gallery Ressort linktext should not be displayed on mobile.')
    assert not gallery_counter.is_displayed(), (
        'Gallery image counter should not be displayed on mobile.')
    assert not gallery_text.is_displayed(), (
        'Gallery description text should not be displayed on mobile.')

    driver.set_window_size(520, 650)
    assert ressort_linktext.is_displayed(), (
        'Gallery Ressort linktext must be displayed on phablet.')
    assert not gallery_counter.is_displayed(), (
        'Gallery image counter should not be displayed on phablet.')
    assert not gallery_text.is_displayed(), (
        'Gallery description text should not be displayed on phablet.')

    driver.set_window_size(768, 960)
    assert ressort_linktext.is_displayed(), (
        'Gallery Ressort linktext must be displayed on tablet.')
    assert gallery_counter.is_displayed(), (
        'Gallery image counter must be displayed on tablet.')
    assert gallery_text.is_displayed(), (
        'Gallery description text must be displayed on tablet.')

    driver.set_window_size(980, 1024)
    assert ressort_linktext.is_displayed(), (
        'Gallery Ressort linktext must be displayed on desktop.')
    assert gallery_counter.is_displayed(), (
        'Gallery image counter must be displayed on desktop.')
    assert gallery_text.is_displayed(), (
        'Gallery description text must be displayed on desktop.')


@pytest.mark.xfail(reason='Fortune favours the fail')
def test_gallery_teaser_shuffles_on_click(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('{}/zeit-online/teaser-gallery-setup'.format(testserver.url))
    teaserbutton = driver.find_element_by_css_selector(
        '.js-gallery-teaser-shuffle')
    teasertext1 = driver.find_element_by_css_selector(
        '.teaser-gallery__heading').text
    teaserbutton.click()

    try:
        WebDriverWait(driver, 2).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '.teaser-gallery__heading')))
    except TimeoutException:
        assert False, 'New teasers not loaded within 2 seconds'
    else:
        teasertext2 = driver.find_element_by_css_selector(
            '.teaser-gallery__heading').text
        assert teasertext1 != teasertext2


def test_homepage_should_have_proper_meetrics_integration(
        testserver, testbrowser):
    browser = testbrowser('/zeit-online/slenderized-index')
    meetrics = browser.cssselect(
        'script[src="http://s62.mxcdn.net/bb-serve/mtrcs_225560.js"]')
    assert len(meetrics) == 1


def test_centerpage_must_not_have_meetrics_integration(
        testserver, testbrowser):
    browser = testbrowser(
        '{}/zeit-online/main-teaser-setup'.format(testserver.url))
    meetrics = browser.cssselect(
        'script[src="http://s62.mxcdn.net/bb-serve/mtrcs_225560.js"]')
    assert len(meetrics) == 0


def test_centerpage_renders_buzzbox_accordion(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-online/buzz-box' % testserver.url)
    try:
        WebDriverWait(driver, 5).until(
            expected_conditions.presence_of_element_located(
                (By.CLASS_NAME, 'buzz-accordion')))
    except TimeoutException:
        assert False, 'Timeout accordion script'
    else:
        slides = driver.find_elements_by_css_selector('.buzz-box__teasers')
        assert len(slides) == 4
        assert slides[0].is_displayed()
        assert not slides[1].is_displayed()
        assert not slides[2].is_displayed()
        assert not slides[3].is_displayed()


def test_non_navigation_centerpage_should_have_minimal_breadcrumbs(
        application, monkeypatch):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/main-teaser-setup')
    monkeypatch.setattr(
        zeit.web.site.view_centerpage.Centerpage, u'ressort', u'moep')
    view = zeit.web.site.view_centerpage.Centerpage(context, mock.Mock())
    assert view.breadcrumbs == [
        ('Start', 'http://xml.zeit.de/index', 'ZEIT ONLINE')]


def test_homepage_should_have_no_breadcrumbs(
        application, monkeypatch):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/index')
    view = zeit.web.site.view_centerpage.Centerpage(context, mock.Mock())
    assert view.breadcrumbs == []


def test_breadcrumbs_should_handle_non_ascii(application, monkeypatch):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/main-teaser-setup')
    monkeypatch.setattr(
        zeit.content.cp.centerpage.CenterPage, u'title', u'umläut')
    monkeypatch.setattr(
        zeit.content.cp.centerpage.CenterPage, u'type', u'topicpage')
    view = zeit.web.site.view_centerpage.Centerpage(context, mock.Mock())
    assert (u'Thema: umläut', None) in view.breadcrumbs


def test_mobile_invisibility(testbrowser):
    browser = testbrowser('/zeit-online/mobile-visible-index')
    region = '#main .cp-region:first-child.mobile-hidden'
    area = '#main .cp-region:nth-child(2) .cp-area:first-child.mobile-hidden'
    teaser = '#main .cp-region:nth-child(2) \
        .cp-area:nth-child(2) article:first-of-type.mobile-hidden'
    assert len(browser.cssselect(region)) == 1
    assert len(browser.cssselect(area)) == 1
    assert len(browser.cssselect(teaser)) == 1


def test_breakpoint_sniffer_script(
        selenium_driver, testserver, monkeypatch, screen_size):

    def tpm(me):
        return True

    monkeypatch.setattr(
        zeit.web.core.view.Base, 'enable_third_party_modules', tpm)

    driver = selenium_driver
    driver.set_window_size(screen_size[0], screen_size[1])
    driver.get('{}/zeit-online/slenderized-index'.format(testserver.url))

    if screen_size[0] == 320:
        assert "mobile" == driver.execute_script(
            "return window.ZMO.breakpoint.get()")
    if screen_size[0] == 520:
        assert "phablet" == driver.execute_script(
            "return window.ZMO.breakpoint.get()")
    if screen_size[0] == 768:
        assert "tablet" == driver.execute_script(
            "return window.ZMO.breakpoint.get()")
    if screen_size[0] == 980:
        assert "desktop" == driver.execute_script(
            "return window.ZMO.breakpoint.get()")


def test_hidden_images_must_not_be_loaded_via_js(
        selenium_driver, testserver, screen_size):

    driver = selenium_driver
    driver.set_window_size(screen_size[0], screen_size[1])
    driver.get('%s/zeit-online/slenderized-index' % testserver.url)

    try:
        WebDriverWait(driver, 2).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '.teaser-fullwidth__media img')))
    except TimeoutException:
        assert False, 'Fullsize Image not loaded within 2 seconds'
    else:
        largeimage = driver.find_elements_by_css_selector(
            'figure.teaser-fullwidth__media img[src]')
        smallimage = driver.find_elements_by_css_selector(
            'figure.teaser-small__media img[src]')

        if screen_size[0] == 320:
            assert len(smallimage) == 0
            assert len(largeimage) == 1
        elif screen_size[0] == 520:
            assert len(smallimage) > 0
            assert len(largeimage) == 1
        elif screen_size[0] == 768:
            assert len(smallimage) > 0
            assert len(largeimage) == 1
        else:
            assert len(smallimage) > 0
            assert len(largeimage) == 1


def test_app_wrapper_script(selenium_driver, testserver):

    driver = selenium_driver
    driver.get(
        '{}/zeit-online/slenderized-index?app-content'.format(testserver.url))

    ressort = driver.execute_script('return window.wrapper.getRessort()')
    assert ressort == 'homepage'


def test_frames_are_placed_correctly(testbrowser):
    browser = testbrowser('/zeit-online/index-with-quizzez')
    frame1 = browser.cssselect('.cp-area--minor > .frame')
    frame2 = browser.cssselect('.cp-area--duo > .frame')
    assert len(frame1) == 1
    assert len(frame2) == 1

    iframe1 = frame1[0].cssselect('iframe.frame__iframe')
    iframe2 = frame2[0].cssselect('iframe.frame__iframe')
    assert len(iframe1) == 1
    assert len(iframe2) == 1

    frameheadline1 = frame1[0].cssselect('h2')
    frameheadline2 = frame2[0].cssselect('h2')
    assert len(frameheadline1) == 1
    assert len(frameheadline2) == 0
    assert frameheadline1[0].text == 'Quiz'

    assert iframe1[0].get('src') == 'http://quiz.zeit.de/#/quiz/103'
    assert iframe2[0].get('src') == 'http://quiz.zeit.de/#/quiz/136'


def test_frame_dimensions(selenium_driver, testserver, screen_size):
    driver = selenium_driver
    driver.set_window_size(screen_size[0], screen_size[1])
    driver.get('{}/zeit-online/index-with-quizzez'.format(testserver.url))

    frame1 = driver.find_element_by_css_selector('.cp-area--minor > .frame')
    frame2 = driver.find_element_by_css_selector('.cp-area--duo > .frame')

    if screen_size[0] == 320:
        assert frame1.size.get('height') == 450
        assert frame2.size.get('height') == 460

    if screen_size[0] == 520:
        assert frame1.size.get('height') == 450
        assert frame2.size.get('height') == 460

    if screen_size[0] == 768:
        assert frame1.size.get('height') == 450

    if screen_size[0] == 980:
        assert frame1.size.get('height') == 450


def test_teaser_for_column_without_authorimage_should_be_rendered_default(
        testbrowser):
    browser = testbrowser('/zeit-online/teaser-columns-without-authorimage')
    teasers = browser.cssselect('main article')
    # we want to be sure that there are teasers at all.
    assert len(teasers) == 10
    for teaser in teasers:
        assert 'teaser' in teaser.get('class')
        assert 'column' not in teaser.get('class')


def test_wrapped_features_are_triggered(testbrowser):
    browser = testbrowser('/zeit-online/slenderized-index')
    assert browser.cssselect('header.header')

    browser = testbrowser('/zeit-online/slenderized-index?app-content')
    assert not browser.cssselect('header.header')
    assert browser.cssselect('body[data-is-wrapped="true"]')


def test_advertorial_page_has_advertorial_label(testbrowser):
    browser = testbrowser('/zeit-online/advertorial-index')
    assert browser.cssselect('.main_nav__ad-label.advertorial__ad-label')
