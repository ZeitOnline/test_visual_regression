# -*- coding: utf-8 -*-
import datetime
import re
import urllib2

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
import lxml.html
import mock
import pyramid.httpexceptions
import pyramid.testing
import pytest
import requests
import zope.component

from zeit.cms.checkout.helper import checked_out
import zeit.cms.interfaces
import zeit.content.cp.centerpage
import zeit.content.volume

import zeit.web.core.centerpage
import zeit.web.core.template
import zeit.web.core.utils
import zeit.web.site.module.playlist
import zeit.web.site.view_centerpage


screen_sizes = ((320, 480, True), (520, 960, True),
                (768, 1024, False), (1000, 1024, False))


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

    request = pyramid.testing.DummyRequest()
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


def test_default_teaser_should_match_css_selectors(application, jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/teaser/default.tpl')

    teaser = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/01')
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/centerpage/index')
    teaser.teaserSupertitle = 'teaserSupertitle'
    teaser.teaserTitle = 'teaserTitle'
    teaser.teaserText = 'teaserText'
    view = mock.Mock()
    view.comment_counts = {'http://xml.zeit.de/zeit-magazin/article/01': 129}
    view.context = cp
    view.request.route_url.return_value = '/'

    area = mock.Mock()
    area.kind = 'solo'

    module = mock.Mock()

    request = mock.Mock()

    html_str = tpl.render(
        teaser=teaser, layout='teaser', view=view, area=area, module=module,
        request=request)
    html = lxml.html.fromstring(html_str).cssselect

    assert len(html('article.teaser h2.teaser__heading')) == 1

    link = html('a.teaser__combined-link')[0]
    assert link.get('href') == '/zeit-magazin/article/01'
    assert link.get('title') == 'teaserSupertitle - teaserTitle'

    link_kicker = html('a.teaser__combined-link span.teaser__kicker')[0]
    assert 'teaserSupertitle' in link_kicker.text_content()

    link_title = html('a.teaser__combined-link span.teaser__title')[0]
    assert link_title.text == 'teaserTitle'

    assert len(html('article > div.teaser__container')) == 1

    teaser_text = html('div.teaser__container > p.teaser__text')[0]
    assert teaser_text.text == 'teaserText'

    assert len(html('div.teaser__container > div.teaser__metadata')) == 1
    byline = html('div.teaser__metadata > span.teaser__byline')[0]
    assert re.sub('\s+', ' ', byline.text).strip() == 'Von Anne Mustermann'

    teaser_co = html('div.teaser__metadata > a.teaser__commentcount')[0]

    assert teaser_co.get('href') == teaser.uniqueId.replace(
        'http://xml.zeit.de', '') + '#comments'
    assert teaser_co.get('title') == 'Kommentare anzeigen'
    assert teaser_co.text == '129 Kommentare'


def test_small_teaser_should_display_no_image_on_mobile(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.set_window_size(320, 480)
    driver.get('%s/zeit-online/slenderized-index' % testserver.url)
    box = driver.find_elements_by_class_name('cp-area--major')[0]
    teaser_image = box.find_elements_by_class_name('teaser-small__media')[0]

    assert teaser_image.is_displayed() is False, 'image is not displayed'


def test_fullwidth_teaser_should_be_rendered(testbrowser):
    browser = testbrowser('/zeit-online/fullwidth-teaser')
    teaser = browser.cssselect('.teaser-fullwidth')
    teaser_column = browser.cssselect('.teaser-fullwidth-column')

    assert len(teaser) == 5
    assert len(teaser_column) == 1


def test_fullwidth_teaser_image_should_have_attributes_for_mobile_variant(
        testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.unset(
        'responsive_image_leadteaser')
    browser = testbrowser('/zeit-online/fullwidth-teaser')
    img = browser.cssselect('.teaser-fullwidth__media-item')[0]
    assert img.get('data-mobile-ratio').startswith('1.77')
    assert 'cp-content/ig-1/wide' in img.get('data-mobile-src')


def test_fullwidth_teaser_image_should_use_mobile_variant_on_mobile(
        selenium_driver, testserver):
    driver = selenium_driver

    driver.set_window_size(screen_sizes[1][0], screen_sizes[1][1])
    driver.get('%s/zeit-online/fullwidth-teaser' % testserver.url)
    img = driver.find_element_by_class_name('teaser-fullwidth__media-item')
    ratio = float(img.size['width']) / img.size['height']
    assert '/wide__' in img.get_attribute('currentSrc'), \
        'wide image variant should be used on mobile devices'
    assert 1.7 < ratio < 1.8, 'mobile ratio should be 16:9-ish'


@pytest.mark.xfail(reason='not testable this way with selenium3/geckodriver')
def test_fullwidth_teaser_image_should_use_desktop_variant_on_desktop(
        selenium_driver, testserver):
    driver = selenium_driver

    driver.set_window_size(screen_sizes[3][0], screen_sizes[3][1])
    driver.get('%s/zeit-online/fullwidth-teaser' % testserver.url)
    img = driver.find_element_by_class_name('teaser-fullwidth__media-item')
    ratio = float(img.size['width']) / img.size['height']
    assert '/cinema__' in img.get_attribute('currentSrc'), \
        'wide image variant should be used on mobile devices'
    assert 2.3 < ratio < 2.4, 'desktop cinema ratio should be 7:3-ish'


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
        assert int(helper.size.get('width')) == int(width * 0.72)

    elif screen_size[0] == 1000:
        width = driver.execute_script(script)
        assert int(helper.size.get('width')) == int(width * 0.6666)


def test_main_teasers_should_be_rendered_correctly(testbrowser):
    browser = testbrowser('/zeit-online/main-teaser-setup')

    articles = browser.cssselect('#main .cp-region .cp-area--major article')
    assert len(articles) == 3


def test_main_teasers_should_have_ids_attached(testbrowser):
    browser = testbrowser('/zeit-online/main-teaser-setup')

    all_articles = len(browser.cssselect('.teaser'))
    articles_with_ids = len(browser.cssselect('.teaser[data-unique-id]'))
    assert all_articles == articles_with_ids, 'We expect all teasers here'


def test_main_teasers_should_have_id_attached(testbrowser):
    browser = testbrowser('/zeit-online/main-teaser-setup')

    body = browser.cssselect(
        'body[data-unique-id="'
        'http://xml.zeit.de/zeit-online/main-teaser-setup"]')
    assert len(body) == 1, 'Body element misses data-attribute unique-id'


def test_main_teasers_should_have_type_attached(testbrowser):
    browser = testbrowser('/zeit-online/main-teaser-setup')

    body = browser.cssselect(
        'body[data-page-type="centerpage"]')
    assert len(body) == 1, 'Body element misses data-attribute page-type'


def test_responsive_image_should_render_correctly(testbrowser):
    browser = testbrowser('/zeit-online/main-teaser-setup')

    image = browser.cssselect(
        '#main .cp-region .cp-area'
        ' article:first-of-type figure.scaled-image'
        ' a > img')
    assert len(image) == 1, 'Only one image for first article'


def test_image_should_be_on_position_b(testbrowser):
    browser = testbrowser('/zeit-online/main-teaser-setup')
    articles = browser.cssselect('#main .cp-region .cp-area article')

    assert articles[0][0][1].tag == 'figure', 'This position should haz image'


def test_image_should_be_on_position_a(testbrowser):
    browser = testbrowser('/zeit-online/main-teaser-setup')
    articles = browser.cssselect('#main .cp-region .cp-area article')

    assert articles[1][0].tag == 'figure', 'An img should be on this position'


def test_responsive_image_should_have_noscript(testbrowser):
    browser = testbrowser('/zeit-online/main-teaser-setup')

    noscript = browser.cssselect(
        '#main .cp-region--duo .scaled-image noscript')
    assert len(noscript) == 3


def test_topic_links_title_schould_have_a_value_and_default_value(application):
    context = zeit.content.cp.centerpage.CenterPage()

    context.topiclink_title = 'My Title'
    topic_links = zeit.web.core.centerpage.TopicLink(context)
    assert topic_links.title == 'My Title'

    context.topiclink_title = None
    topic_links = zeit.web.core.centerpage.TopicLink(context)
    assert topic_links.title == 'Schwerpunkte'


def test_centerpage_view_should_have_topic_links(
        application, preserve_settings):
    settings = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    settings['transform_to_secure_links_for'] = 'www.zeit.de'

    mycp = zeit.content.cp.centerpage.CenterPage()
    mycp.topiclink_label_1 = 'Label 1'
    mycp.topiclink_url_1 = 'http://www.zeit.de/thema/foo'
    mycp.topiclink_label_2 = 'Label 2'
    mycp.topiclink_url_2 = 'http://link_2'
    mycp.topiclink_label_3 = 'Label 3'
    mycp.topiclink_url_3 = 'http://link_3'

    topic_links = list(zeit.web.core.centerpage.TopicLink(mycp))

    assert topic_links == [('Label 1', 'https://www.zeit.de/thema/foo'),
                           ('Label 2', 'http://link_2'),
                           ('Label 3', 'http://link_3')]


def test_cp_areas_should_be_rendered_correctly(testbrowser):
    browser = testbrowser('/zeit-online/index')

    fullwidth = browser.cssselect('.cp-area.cp-area--solo .teaser-fullwidth')
    content = browser.cssselect('.cp-area.cp-area--major')
    informatives = browser.cssselect('.cp-area.cp-area--minor')

    assert len(fullwidth) == 1
    assert len(content) == 1
    assert len(informatives) == 1


def test_column_teaser_should_render_series_element(testbrowser):
    browser = testbrowser('/zeit-online/journalistic-formats')

    col_element = browser.cssselect(
        '.teaser-fullwidth-column__series-label')[0]
    assert col_element.text == u'Fünf vor acht'


def test_teaser_for_column_should_render_square_image_variant(testbrowser):
    browser = testbrowser('/zeit-online/journalistic-formats')

    teaser_img = browser.cssselect('.teaser-small-column__media-item')[0]
    assert teaser_img.get('src') == (
        'http://localhost/zeit-online/cp-content/ig-3/square__460x460')


def test_series_teaser_should_render_series_element(testbrowser):
    browser = testbrowser('/zeit-online/journalistic-formats')
    series_element = browser.cssselect('.teaser-large__series-label')
    assert series_element[0].text == 'Serie: App-Kritik'


def test_podcast_series_fallback_teaser_image_is_used(testbrowser):
    browser = testbrowser('/zeit-online/centerpage/podcast-teaser-fallback')
    teaser_image_one = browser.cssselect('.teaser-square__media-item')[0]
    teaser_image_two = browser.cssselect('.teaser-square__media-item')[1]
    assert teaser_image_one.get('src').endswith(
        "podcast-illustration-fallback/square__460x460__EEB200")
    assert teaser_image_two.get('src').endswith(
        "podcast-illustration/square__460x460__EEB200")


def test_small_teaser_should_have_responsive_layout(
        selenium_driver, testserver, screen_size):

    driver = selenium_driver
    driver.set_window_size(screen_size[0], screen_size[1])
    driver.get('%s/zeit-online/slenderized-index' % testserver.url)

    script = ('var width = window.getComputedStyle('
              'document.querySelector(".teaser-small__media-container")'
              ').getPropertyValue("width"); return parseInt(width, 10);')
    width = driver.execute_script(script)

    img_box = driver.find_elements_by_class_name('teaser-small__media')[0]

    if screen_size[0] == 320:
        assert not img_box.is_displayed(), 'no image should be shown on mobile'
    elif screen_size[0] == 520:
        assert width == 150
    elif screen_size[0] == 768:
        assert width == 150
    else:
        assert width == 250


def test_snapshot_morelink_text_icon_switch(
        selenium_driver, testserver, screen_size):
    driver = selenium_driver
    driver.set_window_size(screen_size[0], screen_size[1])
    driver.get('%s/zeit-online/teaser-gallery-setup' % testserver.url)
    linkdisplay = driver.execute_script(
        'return window.getComputedStyle('
        'document.querySelector(".snapshot .section-heading__text")'
        ').getPropertyValue("display")')
    if screen_size[0] == 320:
        assert linkdisplay == u'none', 'Linktext not hidden on mobile'
    else:
        assert linkdisplay == u'inline', 'Linktext hidden on other than mobile'


def test_snapshot_should_show_first_gallery_image(testbrowser):
    browser = testbrowser('/zeit-online/teaser-gallery-setup')
    image = browser.cssselect('.snapshot__media-item')[0]
    assert '462507429-540x304.jpg' in image.get('src')


def test_snapshot_media_link_should_have_title(testbrowser):
    browser = testbrowser('/zeit-online/teaser-gallery-setup')
    media_link_title = browser.cssselect(
        '.snapshot__media-container a')[0].get('title')
    assert media_link_title == 'Automesse Detroit - Von Krise keine Spur mehr'


def test_snapshot_should_display_correct_teaser_title(testbrowser):
    browser = testbrowser('/zeit-online/teaser-gallery-setup')
    title = browser.cssselect('.snapshot .section-heading__title')[0]
    assert title.text.strip() == 'Momentaufnahme'


def test_snapshot_should_display_correct_image_caption(testbrowser):
    browser = testbrowser('/zeit-online/teaser-gallery-setup')
    caption = browser.cssselect('.snapshot__text')[0]
    assert (caption.text.strip() ==
            u'Ford präsentiert auf der Automesse in Detroit'
            u' den neuen Pick-up F-150.')


def test_snapshot_should_display_copyright_with_nonbreaking_space(testbrowser):
    browser = testbrowser('/zeit-online/teaser-gallery-setup')
    copyright = browser.cssselect('.snapshot__copyright')[0]
    assert (copyright.text_content().strip() ==
            u'\xa9\xa0Xinhua/Zhang Wenkui/Reuters')


def test_small_teaser_without_image_has_no_padding_left(
        selenium_driver, testserver):

    driver = selenium_driver
    driver.set_window_size(768, 600)
    driver.get('%s/zeit-online/teaser-serie-setup' % testserver.url)
    teaser = driver.find_element_by_css_selector(
        '*[data-unique-id*="/article-ohne-bild"] .teaser-small__container')
    assert int(teaser.location.get('x')) == 20


def test_parquet_region_list_should_have_regions(application):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/parquet-teaser-setup')
    view = zeit.web.site.view_centerpage.LegacyCenterpage(
        cp, pyramid.testing.DummyRequest())
    assert len(view.region_list_parquet) == 3, (
        'View contains %s parquet regions instead of 4' % len(
            view.region_list_parquet))


def test_parquet_regions_should_have_one_area_each(application):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/parquet-teaser-setup')
    view = zeit.web.site.view_centerpage.LegacyCenterpage(
        cp, pyramid.testing.DummyRequest())
    assert [1, 1, 1] == [len(region) for region in view.region_list_parquet]


def test_parquet_region_areas_should_have_multiple_modules_each(application):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/parquet-teaser-setup')
    view = zeit.web.site.view_centerpage.LegacyCenterpage(
        cp, pyramid.testing.DummyRequest())
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

    driver.set_window_size(1000, 1024)
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

    driver.set_window_size(1000, 1024)
    assert small_teaser.is_displayed(), (
        'Small parquet teaser must show it‘s image on desktop.')


def test_playlist_video_series_should_be_available(application):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/video/playlist/36516804001')
    playlist = zeit.web.site.module.playlist.Playlist(content)
    assert len(playlist.video_series_list) == 24


def test_videostage_should_have_right_video_count(testbrowser):
    browser = testbrowser('/zeit-online/video-stage')
    videos = browser.cssselect('#video-stage article')
    assert len(videos) == 4, 'We expect 4 videos in video-stage'


def test_videostage_should_have_correct_images(testbrowser):
    browser = testbrowser('/zeit-online/video-stage')
    video_images = browser.cssselect('#video-stage img')
    assert len(video_images) == 4
    vi0 = video_images[0].get('src')
    assert '/video/2014-01/1953013471001/imagegroup/' in vi0
    vi1 = video_images[1].get('src')
    assert '/video/2014-01/3035864892001/imagegroup/' in vi1
    vi2 = video_images[2].get('src')
    assert '/zeit-online/video/3537342483001/imagegroup/' in vi2
    vi3 = video_images[3].get('src')
    assert '/video/2014-01/3089721834001/imagegroup/' in vi3


def test_videostage_videos_should_have_video_ids(testbrowser):
    browser = testbrowser('/zeit-online/video-stage')
    videos = browser.cssselect('#video-stage article')
    for video in videos:
        assert video.get('data-video-id')


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


def test_videostage_thumbnail_should_be_replaced(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-online/video-stage' % testserver.url)
    article = driver.find_element_by_css_selector(
        '#video-stage .video-large')
    videolink = driver.find_element_by_css_selector(
        '#video-stage .video-large figure')
    thumbnail = article.find_element_by_css_selector(
        '.video-thumbnail__media-item')
    videolink.click()
    try:
        WebDriverWait(driver, 10).until(
            expected_conditions.staleness_of(thumbnail))
        assert True
    except TimeoutException:
        assert False, 'Thumbnail not replaced by video'


def test_videostage_has_zon_svg_logo(testbrowser):
    browser = testbrowser('/zeit-online/video-stage')
    logo = browser.cssselect('svg.video-stage-heading__logo')
    assert len(logo) == 1


def test_module_printbox_should_produce_teaser_image(
        application, dummy_request):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/index')
    view = zeit.web.site.view_centerpage.LegacyCenterpage(
        cp, dummy_request)
    printbox = zeit.web.core.centerpage.get_module(view.module_printbox)
    image = zeit.web.core.template.get_image(
        printbox, name='content', fallback=False)
    assert zeit.web.core.interfaces.IImage.providedBy(image)


def test_homepage_identifies_itself_as_homepage(testserver):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/index')
    request = pyramid.testing.DummyRequest()
    view = zeit.web.site.view_centerpage.Centerpage(cp, request)
    assert view.is_hp is True
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/main-teaser-setup')
    view = zeit.web.site.view_centerpage.Centerpage(cp, request)
    assert view.is_hp is False


def test_homepage_ressort_is_homepage(application):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/index')
    view = zeit.web.site.view_centerpage.Centerpage(
        cp, pyramid.testing.DummyRequest())
    assert view.ressort == 'homepage'


def test_linkobject_teaser_should_contain_supertitle(testbrowser):
    browser = testbrowser('/zeit-online/index')
    uid = 'http://xml.zeit.de/zeit-online/cp-content/link_teaser'
    kicker = browser.cssselect('.teaser-small[data-unique-id="{}"] '
                               '.teaser-small__kicker'.format(uid))[0]
    assert kicker.text.strip() == 'Freier Teaser Kicker'


def test_blog_teaser_should_have_specified_markup(testbrowser):
    browser = testbrowser('/zeit-online/journalistic-formats')
    uid = 'http://xml.zeit.de/blogs/nsu-blog-bouffier'
    teaser = browser.cssselect(
        '.teaser-large[data-unique-id="{}"] '.format(uid))[0]

    kicker = teaser.cssselect('.teaser-large__kicker--blog')[0]
    assert kicker.text.strip() == 'Zeugenvernehmung'

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


def test_gallery_teaser_should_contain_supertitle(testbrowser):
    browser = testbrowser('/zeit-online/index')
    uid = 'http://xml.zeit.de/galerien/fs-desktop-schreibtisch-computer'
    kicker = browser.cssselect('.teaser-small[data-unique-id="{}"] '
                               '.teaser-small__kicker'.format(uid))[0]
    assert 'Desktop-Bilder' in kicker.text_content()


def test_homepage_should_have_nav_tags(testbrowser):
    browser = testbrowser('/zeit-online/index')

    assert browser.cssselect('.nav__tags')
    assert browser.cssselect('.nav__label')[0].text == 'Schwerpunkte'

    tags = browser.cssselect('.nav__tag')
    assert len(tags) == 3
    assert tags[0].get('href').endswith(
        '/schlagworte/organisationen/islamischer-staat/index')
    assert tags[0].text == 'Islamischer Staat'


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
        assert int(round(teaser.size.get('width'))) == (int(
            round((main_width - gutter_width) / 3.0) - gutter_width))
    elif screen_size[0] == 1000:
        assert int(round(teaser.size.get('width'))) == (int(
            round((main_width - gutter_width) / 3.0) - gutter_width))


def test_canonical_ruleset_on_cps(testbrowser, data_solr):
    browser = testbrowser('/dynamic/ukraine')

    # no param
    link = browser.cssselect('link[rel="canonical"]')
    assert link[0].get('href') == 'http://localhost/dynamic/ukraine'

    # p param
    browser = testbrowser('/dynamic/ukraine?p=2')
    link = browser.cssselect('link[rel="canonical"]')
    assert link[0].get('href') == 'http://localhost/dynamic/ukraine?p=2'

    # several params
    browser = testbrowser('/dynamic/ukraine?p=2&a=0#comment')
    link = browser.cssselect('link[rel="canonical"]')
    assert link[0].get('href') == 'http://localhost/dynamic/ukraine?a=0&p=2'


def test_canonical_ruleset_on_article_pages(testbrowser):
    browser = testbrowser('/zeit-online/index')
    link = browser.cssselect('link[rel="canonical"]')
    assert link[0].get('href') == 'http://localhost/zeit-online/index'


def test_canonical_ruleset_on_ranking_pages(testbrowser, data_solr):
    browser = testbrowser('/suche/index')
    link = browser.cssselect('link[rel="canonical"]')
    assert link[0].get('href') == 'http://localhost/suche/index'

    browser = testbrowser('/suche/index?p=2')
    link = browser.cssselect('link[rel="canonical"]')
    assert link[0].get('href') == 'http://localhost/suche/index?p=2'

    browser = testbrowser('/suche/index?q=s%C3%BC%C3%9F')
    link = browser.cssselect('link[rel="canonical"]')[0]
    assert link.get('href') == 'http://localhost/suche/index?q=s%C3%BC%C3%9F'

    browser = testbrowser('/dynamic/ukraine')
    link = browser.cssselect('link[rel="canonical"]')
    assert link[0].get('href') == 'http://localhost/dynamic/ukraine'

    browser = testbrowser('/dynamic/ukraine?p=2')
    link = browser.cssselect('link[rel="canonical"]')
    assert link[0].get('href') == 'http://localhost/dynamic/ukraine?p=2'


def test_robots_rules_for_paginated_centerpages(testbrowser):
    browser = testbrowser('/dynamic/umbrien')
    assert browser.xpath('//meta[@name="robots"]/@content')[0] == (
        'index,follow,noarchive')

    browser = testbrowser('/dynamic/umbrien?p=2')
    assert browser.xpath('//meta[@name="robots"]/@content')[0] == (
        'noindex,follow,noarchive')


def test_robots_rules_for_angebote_paths(application):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/index')
    request = pyramid.testing.DummyRequest()

    # usual angebot
    request.path = '/angebote/immobilien/test'
    view = zeit.web.site.view_centerpage.Centerpage(cp, request)
    assert view.meta_robots == 'index,nofollow,noarchive'

    # partnersuche
    request.path = '/angebote/partnersuche/test'
    view = zeit.web.site.view_centerpage.Centerpage(cp, request)
    assert view.meta_robots == 'index,follow,noarchive'


def test_robots_rules_for_diverse_paths(application):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/index')
    request = pyramid.testing.DummyRequest()
    request.url = 'http://localhost'

    # test folder
    request.path = '/test/foo'
    view = zeit.web.site.view_centerpage.Centerpage(cp, request)
    assert view.meta_robots == 'noindex,follow,noarchive'

    # templates folder
    request.path = '/templates/article-01'
    view = zeit.web.site.view_centerpage.Centerpage(cp, request)
    assert view.meta_robots == 'noindex,follow,noarchive'

    # banner folder
    request.path = '/banner/iqd'
    view = zeit.web.site.view_centerpage.Centerpage(cp, request)
    assert view.meta_robots == 'noindex,follow,noarchive'

    # autoren folder
    request.path = '/autoren/register/A'
    view = zeit.web.site.view_centerpage.Centerpage(cp, request)
    assert view.meta_robots == 'noindex,follow,noarchive'

    # any folder
    request.path = '/any/article-01'
    view = zeit.web.site.view_centerpage.Centerpage(cp, request)
    assert view.meta_robots == 'index,follow,noarchive'


def test_meta_rules_for_keyword_paths(application):
    request = pyramid.testing.DummyRequest()

    # person
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/dynamic/paul-auster')
    view = zeit.web.core.view_centerpage.Centerpage(cp, request)
    assert view.pagetitle == 'Paul Auster - News und Infos | ZEIT ONLINE'
    assert view.pagedescription == (
        'Hier finden Sie alle News und Hintergrund-Informationen '
        'von ZEIT ONLINE zu Paul Auster.')

    # location
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/dynamic/umbrien')
    view = zeit.web.core.view_centerpage.Centerpage(cp, request)
    assert view.pagetitle == 'Umbrien - News und Infos | ZEIT ONLINE'
    assert view.pagedescription == (
        'Hier finden Sie alle News und Hintergrund-Informationen '
        'von ZEIT ONLINE zu Umbrien.')

    # organisation
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/dynamic/bayerische-landesbank')
    view = zeit.web.core.view_centerpage.Centerpage(cp, request)
    assert view.pagetitle == (
        'Bayerische Landesbank - News und Infos | ZEIT ONLINE')
    assert view.pagedescription == (
        'Hier finden Sie alle News und Hintergrund-Informationen '
        'von ZEIT ONLINE zu dem Thema Bayerische Landesbank.')

    # subject
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/dynamic/ausdauersport')
    view = zeit.web.core.view_centerpage.Centerpage(cp, request)
    assert view.pagetitle == 'Ausdauersport - News und Infos | ZEIT ONLINE'
    assert view.pagedescription == (
        'Hier finden Sie alle News und Hintergrund-Informationen '
        'von ZEIT ONLINE zu dem Thema Ausdauersport.')


def test_newsticker_should_have_expected_dom(testbrowser, data_solr):
    browser = testbrowser('/zeit-online/news-teaser')

    cols = browser.cssselect('.cp-area--newsticker .newsticker__column')
    assert len(cols) == 2
    teaser = browser.cssselect('.cp-area--newsticker article.newsteaser')
    assert len(teaser) == 8
    assert len(teaser[0].cssselect('time')) == 1
    assert len(
        teaser[0].cssselect('a .newsteaser__text .newsteaser__kicker')) == 1
    assert len(
        teaser[0].cssselect('a .newsteaser__text .newsteaser__title')) == 1
    assert len(
        teaser[0].cssselect('a .newsteaser__text .newsteaser__product')) == 1


def test_newspage_has_expected_elements(testbrowser, data_es):
    browser = testbrowser('/news/index')
    area = browser.cssselect('.cp-area--overview')[0]
    assert len(area.cssselect('.pager--overview')) == 1
    assert len(area.cssselect('.newsteaser')) > 1


def test_servicebox_present_in_wide_breakpoints(
        selenium_driver, testserver, screen_size):
    driver = selenium_driver
    driver.set_window_size(screen_size[0], screen_size[1])
    driver.get(
        '%s/zeit-online/slenderized-index-with-newsbox' % testserver.url)
    servicebox = driver.find_element_by_id('servicebox')

    if screen_size[0] == 320:
        assert servicebox.is_displayed() is False, 'Servicebox displayed'
    if screen_size[0] == 520:
        assert servicebox.is_displayed() is False, 'Servicebox displayed'
    if screen_size[0] == 768:
        assert servicebox.is_displayed() is True, 'Servicebox not displayed'
    if screen_size[0] == 1000:
        assert servicebox.is_displayed() is True, 'Servicebox not displayed'


def test_centerpage_area_should_render_in_isolation(testbrowser):
    browser = testbrowser('/index/area/id-5fe59e73-e388-42a4-a8d4-'
                          '750b0bf96812')
    select = browser.cssselect
    assert len(select('div.cp-area.cp-area--gallery')) == 1
    assert len(select('article.teaser-gallery')) == 2
    assert browser.headers['X-Robots-Tag'] == 'noindex'


def test_centerpage_area_should_render_on_index(testbrowser):
    browser = testbrowser('/index/area/no-1')
    select = browser.cssselect
    assert len(select('.cp-area.cp-area--solo')) == 1
    assert len(select('article.teaser-fullwidth')) == 1


def test_centerpage_biga_area_should_render_in_isolation_with_page_param(
        testbrowser):
    browser = testbrowser('/index/area/id-5fe59e73-e388-42a4-a8d4-'
                          '750b0bf96812?p=http://xml.zeit.de/galerien/'
                          'bg-automesse-detroit-2014-usa')
    teaser_second_page = browser.cssselect('.teaser-gallery__title')[0]
    assert teaser_second_page.text == 'Immer nur das Meer sehen'


def test_centerpage_invalid_area_id_should_404(testbrowser):
    with pytest.raises(urllib2.HTTPError) as info:
        testbrowser('/index/area/not-an-id')
    assert info.value.getcode() == 404


def test_centerpage_should_render_bam_style_buzzboxes(testbrowser):
    browser = testbrowser('/zeit-online/zeitonline')
    assert browser.cssselect('.buzz-box')
    assert len(browser.cssselect('.buzz-box__teasers article')) == 3


def test_teaser_buzzbox_link_title_should_match_kicker_and_headline(
        testbrowser):
    browser = testbrowser('/zeit-online/buzz-box')
    figure_links = browser.cssselect('.teaser-buzzboard__media-container a')
    heading_links = browser.cssselect(
        '.teaser-buzzboard__media ~ .teaser-buzzboard__container a ')

    assert len(figure_links) == len(heading_links)

    for index, link in enumerate(figure_links):
        assert link.get('title') == heading_links[index].get('title')


def test_centerpage_square_teaser_has_pixelperfect_image(testbrowser):
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


def test_gallery_teaser_exists(testbrowser):
    browser = testbrowser('/zeit-online/teaser-gallery-setup')
    regions = browser.cssselect('.cp-region--gallery')
    areas = regions[0].cssselect('.cp-area--gallery')
    teasers = areas[0].cssselect('.teaser-gallery ')
    assert len(teasers) == 2


def test_gallery_teaser_has_ressort_heading(testbrowser):
    select = testbrowser('/zeit-online/teaser-gallery-setup').cssselect
    title = select('.cp-area--gallery .section-heading__title')
    assert "Fotostrecken" in title[0].text


def test_gallery_teaser_should_hide_duplicates(testbrowser):
    browser = testbrowser('/zeit-online/teaser-gallery-setup')

    refcp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/foto/index')
    first = zeit.content.cp.interfaces.ITeaseredContent(refcp).next()

    assert first.uniqueId != browser.cssselect(
        '.cp-area--gallery article')[0].get('data-unique-id')


def test_gallery_teaser_has_correct_elements(testbrowser):
    wanted = 2
    browser = testbrowser('/zeit-online/teaser-gallery-setup')
    area = browser.cssselect('.cp-area--gallery')[0]

    assert len(area.cssselect('.teaser-gallery')) == wanted
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

    driver.set_window_size(1000, 1024)
    assert ressort_linktext.is_displayed(), (
        'Gallery Ressort linktext must be displayed on desktop.')
    assert gallery_counter.is_displayed(), (
        'Gallery image counter must be displayed on desktop.')
    assert gallery_text.is_displayed(), (
        'Gallery description text must be displayed on desktop.')


def test_gallery_teaser_loads_next_page_on_click(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('{}/zeit-online/teaser-gallery-setup'.format(testserver.url))
    teaserbutton = driver.find_element_by_css_selector(
        '.js-bar-teaser-paginate')
    teaserbutton.click()

    condition = expected_conditions.text_to_be_present_in_element((
        By.CSS_SELECTOR, '.teaser-gallery__title'),
        'Immer nur das Meer sehen')
    assert WebDriverWait(driver, 5).until(condition), (
        'New teasers not loaded within 5 seconds')

    new_teaser_links = driver.find_elements_by_css_selector(
        '.teaser-gallery__combined-link')
    assert new_teaser_links[0].get_attribute('href').endswith(
        '/zeit-online/gallery/england-meer-strand-menschen-fs')
    assert new_teaser_links[1].get_attribute('href').endswith(
        '/zeit-online/gallery/google-neuronale-netzwerke-fs')
    assert teaserbutton.get_attribute('data-sourceurl').endswith(
        'teaser-gallery-setup/area/id-5fe59e73-e388-42a4-a8d4-750b0bf96812?p=')


def test_homepage_should_have_proper_meetrics_integration(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set('third_party_modules')
    browser = testbrowser('/zeit-online/slenderized-index')
    meetrics = browser.cssselect(
        'script[src="//s62.mxcdn.net/bb-serve/mtrcs_225560.js"]')
    assert len(meetrics) == 1


def test_centerpage_should_have_meetrics_integration(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set('third_party_modules')
    browser = testbrowser('/zeit-online/main-teaser-setup')
    meetrics = browser.cssselect(
        'script[src="//s62.mxcdn.net/bb-serve/mtrcs_225560.js"]')
    assert len(meetrics) == 1


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


def test_non_navigation_centerpage_should_have_no_breadcrumbs(
        application, monkeypatch):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/main-teaser-setup')
    monkeypatch.setattr(
        zeit.web.site.view_centerpage.Centerpage, u'ressort', u'moep')
    view = zeit.web.site.view_centerpage.Centerpage(
        context, pyramid.testing.DummyRequest())
    assert view.breadcrumbs == []


def test_homepage_should_have_no_breadcrumbs(
        application, monkeypatch):
    context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/index')
    view = zeit.web.site.view_centerpage.Centerpage(
        context, pyramid.testing.DummyRequest())
    assert view.breadcrumbs == []


def test_breadcrumbs_should_handle_non_ascii(application, monkeypatch):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/main-teaser-setup')
    monkeypatch.setattr(
        zeit.content.cp.centerpage.CenterPage, u'supertitle', u'umläut')
    monkeypatch.setattr(
        zeit.content.cp.centerpage.CenterPage, u'type', u'manualtopic')
    view = zeit.web.site.view_centerpage.Centerpage(
        context, pyramid.testing.DummyRequest())
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

    driver = selenium_driver
    driver.set_window_size(screen_size[0], screen_size[1])
    driver.get('{}/zeit-online/slenderized-index'.format(testserver.url))

    if screen_size[0] == 320:
        assert "mobile" == driver.execute_script(
            "return window.Zeit.breakpoint.get()")
    if screen_size[0] == 520:
        assert "phablet" == driver.execute_script(
            "return window.Zeit.breakpoint.get()")
    if screen_size[0] == 768:
        assert "tablet" == driver.execute_script(
            "return window.Zeit.breakpoint.get()")
    if screen_size[0] == 1000:
        assert "desktop" == driver.execute_script(
            "return window.Zeit.breakpoint.get()")


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
            'figure.teaser-fullwidth__media img[src^="http"]')
        smallimage = driver.find_elements_by_css_selector(
            'figure.teaser-small__media img[src^="http"]')

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


def test_quiz_frames_are_placed_correctly(testbrowser):
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

    assert iframe1[0].get('src') == 'http://quiz.zeit.de/#/quiz/103?embedded'
    assert iframe2[0].get('src') == 'http://quiz.zeit.de/#/quiz/136?embedded'


def test_quiz_frame_dimensions(selenium_driver, testserver, screen_size):
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

    if screen_size[0] == 1000:
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
    assert 'window.wrapper' in browser.contents
    assert 'isWrapped: true,' in browser.cssselect('head')[0].text_content()


def test_app_user_is_back_is_working(selenium_driver, testserver):
    driver = selenium_driver
    driver.set_window_size(375, 667)
    script = 'return window.Zeit.appUserIsBack(123456789)'
    driver.get(
        '{}/zeit-online/slenderized-index?app-content&force-userisback'.format(
            testserver.url))
    driver.execute_script(script)
    try:
        WebDriverWait(driver, 2).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '.app-user-is-back')))
        assert True
    except TimeoutException:
        assert False, 'appUserIsBack message not shown within 2 seconds'


def test_advertorial_page_has_advertorial_label(testbrowser):
    browser = testbrowser('/zeit-online/advertorial-index')
    assert browser.cssselect('.header__ad-label')


def test_standard_teasers_have_meetrics_attribute(testbrowser):
    browser = testbrowser('/zeit-online/basic-teasers-setup')

    fullwidth = browser.cssselect('.teaser-fullwidth')
    large = browser.cssselect('.teaser-large')
    small = browser.cssselect('.teaser-small')
    square = browser.cssselect('.teaser-square')
    buzz = browser.cssselect('.teaser-buzz')

    assert fullwidth[0].get('data-meetrics') == 'solo'
    assert large[0].get('data-meetrics') == 'major'
    assert large[1].get('data-meetrics') == 'parquet'
    assert small[0].get('data-meetrics') == 'major'
    assert small[4].get('data-meetrics') == 'parquet'
    assert square[0].get('data-meetrics') == 'minor'
    assert square[1].get('data-meetrics') == 'duo'
    assert not buzz[0].get('data-meetrics')


def test_video_teasers_have_meetrics_attribute(testbrowser):
    browser = testbrowser('/zeit-online/video-stage')

    large = browser.cssselect('.video-large')
    small = browser.cssselect('.video-small')

    assert large[0].get('data-meetrics') == 'solo'
    assert small[0].get('data-meetrics') == 'solo'


def test_topic_teasers_have_meetrics_attribute(testbrowser):
    browser = testbrowser('/zeit-online/topic-teaser')

    large = browser.cssselect('.teaser-topic-main')
    small = browser.cssselect('.teaser-topic-item')

    assert large[0].get('data-meetrics') == 'topic'
    assert small[0].get('data-meetrics') == 'topic'


def test_author_teaser_is_rendered_in_minor_and_duo(testbrowser):
    browser = testbrowser('/zeit-online/author-teaser')
    assert len(browser.cssselect('.cp-area--minor .teaser-author')) == 3
    assert len(browser.cssselect('.cp-area--duo .teaser-author')) == 2


def test_author_teaser_is_not_rendered_in_major(testbrowser):
    browser = testbrowser('/zeit-online/author-teaser')
    author = browser.cssselect('.cp-area--major .teaser-author')
    assert len(author) == 0


def test_all_areas_have_clicktrack_attribute(testbrowser):
    browser = testbrowser('/zeit-online/basic-teasers-setup')
    areas = browser.cssselect('.cp-area')
    assert len(areas)

    for area in areas:
        assert area.get('data-ct-context') != ''


def test_adtile12_from_cp_extra_is_there(testbrowser):
    browser = testbrowser('/zeit-online/slenderized-centerpage')
    assert browser.cssselect('#ad-desktop-12')


def test_adtile4_from_cp_extra_is_there(testbrowser):
    browser = testbrowser('/zeit-online/centerpage/centerpage')
    assert browser.cssselect('#ad-desktop-4')


def test_adtile9_from_cp_extra_is_there(testbrowser):
    browser = testbrowser('/zeit-online/parquet')
    assert browser.cssselect('#ad-desktop-9')


def test_news_teaser_date_and_reference(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/teaser/zon-newsteaser.tpl')
    request = pyramid.testing.DummyRequest()
    view = mock.Mock()
    view.request = request
    area = mock.Mock()
    area.kind = 'solo'

    url = 'http://xml.zeit.de/zeit-online/article/eilmeldungsartikel'
    teaser = zeit.cms.interfaces.ICMSContent(url)
    html_str = tpl.render(teaser=teaser, view=view, area=area)
    html = lxml.html.fromstring(html_str)
    datetime = html.cssselect('.newsteaser__time')
    product = html.cssselect('.newsteaser__product')

    assert datetime[0].text.strip() == '19:17'
    assert product[0].text == 'ZEIT ONLINE'

    url = 'http://xml.zeit.de/zeit-online/article/afp'
    teaser = zeit.cms.interfaces.ICMSContent(url)
    html_str = tpl.render(teaser=teaser, view=view, area=area)
    html = lxml.html.fromstring(html_str)
    datetime = html.cssselect('.newsteaser__time')
    product = html.cssselect('.newsteaser__product')

    assert datetime[0].text.strip() == '11:59'
    assert product[0].text == 'AFP'

    url = 'http://xml.zeit.de/zeit-online/article/dpa'
    teaser = zeit.cms.interfaces.ICMSContent(url)
    html_str = tpl.render(teaser=teaser, view=view, area=area)
    html = lxml.html.fromstring(html_str)
    datetime = html.cssselect('.newsteaser__time')
    product = html.cssselect('.newsteaser__product')

    assert datetime[0].text.strip() == '22:46'
    assert product[0].text == 'DPA'


def test_cp_does_not_render_image_if_expired(testbrowser):
    with mock.patch('zeit.web.core.image.ImageExpiration.seconds', new=-1):
        browser = testbrowser('/zeit-online/basic-teasers-setup')
        assert '/zeit-online/cp-content/ig-2' not in browser.contents


def test_zplus_parquet_has_own_styles(testbrowser):
    browser = testbrowser('/zeit-online/parquet')

    area = browser.cssselect('.cp-area--zplus-parquet')[0]
    logo = area.cssselect('.parquet-meta__logo--zplus')
    more_link = area.cssselect('.parquet-meta__more-link--zplus')

    assert len(logo)
    assert len(more_link)


def test_zmo_parquet_has_zmo_styles(testbrowser):
    browser = testbrowser('/zeit-online/parquet')

    area = browser.cssselect('.cp-area--zmo-parquet')[0]
    zmo_title = area.cssselect('.parquet-meta__title--zmo')
    zmo_logo = area.cssselect('.parquet-meta__logo--zmo')
    teasers = area.cssselect('article')

    assert len(zmo_title)
    assert len(zmo_logo)
    assert len(teasers) == 3

    for teaser in teasers:
        kicker_classname = teaser.cssselect(
            '.teaser-small__kicker')[0].get('class')
        assert 'teaser-small__kicker--zmo' in kicker_classname
        assert 'teaser-small__kicker--zmo-parquet' in kicker_classname


def test_jobbox_is_displayed_correctly(testbrowser):
    browser = testbrowser('/zeit-online/jobbox')

    # in main area
    box = browser.cssselect('.jobbox--major')[0]
    assert len(box.cssselect('.jobbox__label'))
    assert len(box.cssselect('.jobbox__kicker'))
    assert len(box.cssselect('.jobbox__job')) == 10
    assert len(box.cssselect('.jobbox__title')) == 10
    assert len(box.cssselect('.jobbox__byline')) == 10
    assert len(box.cssselect('.jobbox__action'))

    # in minor area
    box = browser.cssselect('.jobbox--minor')[0]
    assert len(box.cssselect('.jobbox__label'))
    assert len(box.cssselect('.jobbox__kicker'))
    assert len(box.cssselect('.jobbox__job')) == 10
    assert len(box.cssselect('.jobbox__title')) == 10
    assert len(box.cssselect('.jobbox__byline')) == 10
    assert len(box.cssselect('.jobbox__action'))

    # in duo area
    box = browser.cssselect('.jobbox--duo')[0]
    assert len(box.cssselect('.jobbox__label'))
    assert len(box.cssselect('.jobbox__header'))
    assert len(box.cssselect('.jobbox__job')) == 10
    assert len(box.cssselect('.jobbox__title')) == 10
    assert len(box.cssselect('.jobbox__byline')) == 10
    assert len(box.cssselect('.jobbox__action'))

    # in parquet area
    box = browser.cssselect('.jobbox--parquet')[0]
    assert len(box.cssselect('.jobbox__label'))
    assert len(box.cssselect('.jobbox__kicker'))
    assert len(box.cssselect('.jobbox__job')) == 10
    assert len(box.cssselect('.jobbox__title')) == 10
    assert len(box.cssselect('.jobbox__byline')) == 10
    assert len(box.cssselect('.jobbox__action'))


def test_jobbox_is_not_displayed_whith_empty_feed(tplbrowser):
    module = mock.Mock()
    module = ()
    browser = tplbrowser(
        'zeit.web.site:templates/inc/module/jobbox_ticker.html',
        module=module)
    assert len(browser.xpath('//html/body/*')) == 0


def test_partnerbox_jobs_is_displayed_correctly(testbrowser):
    browser = testbrowser('/zeit-online/partnerbox-jobs')

    # in main area
    box = browser.cssselect('.partnerbox')[0]
    assert len(box.cssselect('.partnerbox__label'))
    assert len(box.cssselect('.partner__action'))
    assert len(box.cssselect('.partner__intro'))
    assert len(box.cssselect('.partner--jobs'))
    assert len(box.cssselect('.partner__kicker-img'))
    assert len(box.cssselect('.partner__kicker-text'))
    assert len(box.cssselect('.partner__dropdown'))
    assert len(box.cssselect('.partner__button'))
    assert len(box.cssselect('.partner__link'))
    assert len(box.cssselect('.partner__dropdown-option')) == 9


def test_partnerbox_jobs_dropdown_works(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-online/partnerbox-jobs' % testserver.url)
    dropdown = driver.find_elements_by_class_name('partner__dropdown')[0]
    button = driver.find_elements_by_class_name('partner__button-text')[0]

    # test without selecting anything
    button.click()
    assert 'jobs.zeit.de' in driver.current_url
    assert 'stellenmarkt.funktionsbox.streifen' in driver.current_url

    # test with selected dropdown
    driver.get('%s/zeit-online/partnerbox-jobs' % testserver.url)
    dropdown = driver.find_elements_by_class_name('partner__dropdown')[0]
    button = driver.find_elements_by_class_name('partner__button-text')[0]

    dropdown.find_element_by_xpath(
        "//option[text()='Kunst & Kultur']").click()
    button.click()
    assert 'stellenmarkt/kultur_kunst' in driver.current_url
    assert 'stellenmarkt.funktionsbox.streifen' in driver.current_url


def test_partnerbox_reisen_is_displayed_correctly(testbrowser):
    browser = testbrowser('/zeit-online/partnerbox-reisen')

    # in main area
    box = browser.cssselect('.partnerbox')[0]
    assert len(box.cssselect('.partnerbox__label'))
    assert len(box.cssselect('.partner__action'))
    assert len(box.cssselect('.partner--reisen'))
    assert len(box.cssselect('.partner__dropdown'))
    assert len(box.cssselect('.partner__dropdown-intro'))
    assert len(box.cssselect('.partner__dropdown-title'))
    assert len(box.cssselect('.partner__button'))
    assert len(box.cssselect('.partner__link'))
    assert len(box.cssselect('.partner__link-icon'))
    assert len(box.cssselect('.partner__dropdown-option')) == 18
    media = box.cssselect('.partner__media-item')
    assert len(media)
    assert media[0].get('src').endswith('/reisebox-image/wide__820x461')


@pytest.mark.xfail(reason='Last test fails on jenkins for unknown reason')
def test_partnerbox_reisen_dropdown_works(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-online/partnerbox-reisen' % testserver.url)
    button = driver.find_element_by_class_name('partner__button-text')

    # test without selecting anything
    button.click()
    assert 'zeitreisen.zeit.de' in driver.current_url
    assert 'display.zeit_online.reisebox.dynamisch' in driver.current_url

    # test with selected dropdown
    driver.get('%s/zeit-online/partnerbox-reisen' % testserver.url)
    dropdown = driver.find_element_by_class_name('partner__dropdown')
    button = driver.find_element_by_class_name('partner__button-text')

    dropdown.find_element_by_xpath(
        "//option[text()='Kulturreisen']").click()
    button.click()

    # Wait until the button is no longer attached to the DOM
    # @see http://www.obeythetestinggoat.com/
    #   how-to-get-selenium-to-wait-for-page-load-after-a-click.html
    try:
        WebDriverWait(driver, 3).until(
            expected_conditions.staleness_of(button))
    except TimeoutException:
        assert False, 'New page not loaded within 3 seconds'
    else:
        assert '/themenreisen/kulturreisen/' in driver.current_url
        assert 'display.zeit_online.reisebox.dynamisch' in driver.current_url


def test_studiumbox_is_displayed_correctly(testbrowser):
    browser = testbrowser('/zeit-online/studiumbox')

    box = browser.cssselect('.studiumbox')[0]
    assert len(box.cssselect('.studiumbox__label'))
    assert len(box.cssselect('.studiumbox__container'))
    assert len(box.cssselect('.studiumbox__headline')) == 3
    assert len(box.cssselect('.studiumbox__content')) == 3
    assert len(box.cssselect('.studiumbox__button')) == 3


def test_studiumbox_changes_tabs(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-online/studiumbox' % testserver.url)
    box = driver.find_element_by_class_name('studiumbox')
    links = box.find_elements_by_tag_name('h2')
    link1 = '#studium-interessenstest'
    link2 = '#studiengangssuche'
    link3 = '#hochschulranking'

    # test initial state
    active_link = links[0]
    link_class = active_link.get_attribute('class')
    link_href = active_link.find_element_by_tag_name('a').get_attribute('href')
    content = (box.find_element_by_class_name('studiumbox__content--clone')
               .get_attribute('id'))
    assert 'studiumbox__headline--active' in link_class
    assert link1 in link_href
    assert content in link1

    # test link2
    active_link = links[1]
    active_link.find_element_by_tag_name('a').click()
    link_class = active_link.get_attribute('class')
    link_href = active_link.find_element_by_tag_name('a').get_attribute('href')
    content = (box.find_element_by_class_name('studiumbox__content--clone')
               .get_attribute('id'))
    assert 'studiumbox__headline--active' in link_class
    assert link2 in link_href
    assert content in link2

    # test link3
    active_link = links[2]
    active_link.find_element_by_tag_name('a').click()
    link_class = active_link.get_attribute('class')
    link_href = active_link.find_element_by_tag_name('a').get_attribute('href')
    content = (box.find_element_by_class_name('studiumbox__content--clone')
               .get_attribute('id'))
    assert 'studiumbox__headline--active' in link_class
    assert link3 in link_href
    assert content in link3


def test_studiumbox_interessentest_works(selenium_driver, testserver):
    driver = selenium_driver
    driver.maximize_window()
    driver.get('%s/zeit-online/studiumbox' % testserver.url)
    box = driver.find_element_by_class_name('studiumbox')
    box.find_elements_by_tag_name('h2')

    # test interessentest
    button = (box.find_element_by_class_name('studiumbox__content--clone')
              .find_element_by_class_name('studiumbox__button'))
    button.click()
    assert ('https://studiengaenge.zeit.de/sit'
            '?wt_zmc=fix.int.zonpmr.zeitde.funktionsbox_studium.sit.teaser.'
            'button.&utm_medium=fix&utm_source=zeitde_zonpmr_int'
            '&utm_campaign=funktionsbox_studium'
            '&utm_content=sit_teaser_button_x' in driver.current_url)


def test_studiumbox_suchmaschine_works(selenium_driver, testserver):
    driver = selenium_driver
    driver.maximize_window()
    driver.get('%s/zeit-online/studiumbox' % testserver.url)
    box = driver.find_element_by_class_name('studiumbox')
    links = box.find_elements_by_tag_name('h2')

    # test suchmaschine
    active_link = links[1].find_element_by_tag_name('a')
    active_link.click()
    form = (box.find_element_by_class_name(
            'studiumbox__content--clone')
            .find_element_by_tag_name('form'))
    input_element = (form.find_element_by_class_name('studiumbox__input'))
    input_element.send_keys('test')
    form.submit()
    assert ('https://studiengaenge.zeit.de/studienangebote'
            '?suche=test&wt_zmc=fix.int.zonpmr.zeitde.funktionsbox_studium'
            '.suma.teaser.button.&utm_medium=fix&utm_source=zeitde_zonpmr_int'
            '&utm_campaign=funktionsbox_studium'
            '&utm_content=suma_teaser_button_x' in driver.current_url)


def test_studiumbox_ranking_works(selenium_driver, testserver):
    driver = selenium_driver
    driver.maximize_window()
    driver.get('%s/zeit-online/studiumbox' % testserver.url)
    box = driver.find_element_by_class_name('studiumbox')
    links = box.find_elements_by_tag_name('h2')

    # test suchmaschine
    active_link = links[2].find_element_by_tag_name('a')
    active_link.click()
    form = (box.find_element_by_class_name(
            'studiumbox__content--clone')
            .find_element_by_tag_name('form'))
    dropdown = (form.find_element_by_class_name('studiumbox__input'))
    dropdown.find_element_by_xpath(
        "//option[text()='BWL']").click()
    form.submit()
    assert ('https://ranking.zeit.de/che/de/rankingunion/show?'
            'esb=24&ab=3&hstyp=1&subfach=&wt_zmc=fix.int.zonpmr.zeitde'
            '.funktionsbox_studium.che.teaser.button.'
            '&utm_medium=fix&utm_source=zeitde_zonpmr_int'
            '&utm_campaign=funktionsbox_studium'
            '&utm_content=che_teaser_button_x' in driver.current_url)


def test_studiumbox_ranking_does_fallback(selenium_driver, testserver):
    driver = selenium_driver
    driver.maximize_window()
    driver.get('%s/zeit-online/studiumbox' % testserver.url)
    box = driver.find_element_by_class_name('studiumbox')
    link = box.find_elements_by_tag_name('h2')[2].find_element_by_tag_name('a')

    # test with hochschulranking
    link.click()
    button = (box.find_element_by_class_name('studiumbox__content--clone')
              .find_element_by_class_name('studiumbox__button'))
    button.click()
    assert ('https://ranking.zeit.de/che/de/faecher'
            '?wt_zmc=fix.int.zonpmr.zeitde.funktionsbox_studium.che.teaser'
            '.button_ohne_fach.x&utm_medium=fix&utm_source=zeitde_zonpmr_int'
            '&utm_campaign=funktionsbox_studium'
            '&utm_content=che_teaser_button_ohne_fach_x' in driver.current_url)


def test_zett_banner_is_displayed(testbrowser):
    browser = testbrowser('/zeit-online/zett-banner')
    box = browser.cssselect('.zett-banner')[0]
    link = box.cssselect('a')[0]
    assert len(box.cssselect('.zett-banner__wrapper'))
    assert ('https://ze.tt/?utm_campaign=zonbanner&utm_content=1'
            '&utm_medium=banner&utm_source=zon') == link.get('href')


def test_zett_parquet_is_rendering(testbrowser):
    browser = testbrowser('/zeit-online/parquet-feeds')

    zett_parquet = browser.cssselect('.cp-area--zett')[0]
    title = zett_parquet.cssselect('.parquet-meta__title')
    logo = zett_parquet.cssselect('.parquet-meta__logo')
    teaser = zett_parquet.cssselect('article')
    more_link = zett_parquet.cssselect('.parquet-meta__more-link--zett')
    links = zett_parquet.cssselect('a')

    assert len(title)
    assert len(logo)
    assert len(more_link)
    assert len(teaser) == 3

    # test campaign parameters
    for link in links:
        assert ('?utm_campaign=ref&utm_content=zett_zon_parkett_teaser_x'
                '&utm_medium=fix&utm_source=zon_zettaudev_int'
                '&wt_zmc=fix.int.zettaudev.zon.ref.zett.zon_parkett.teaser.x'
                ) in link.get('href')


def test_zett_large_teaser_is_displayed_in_parquet(testbrowser):
    browser = testbrowser('/zeit-online/parquet')
    zett_parquet = browser.cssselect('.cp-area--zett')[0]
    teaser = zett_parquet.cssselect('.teaser-large')
    assert len(teaser) == 1


def test_zett_parquet_teaser_kicker_should_be_styled(testbrowser):
    browser = testbrowser('/zeit-online/parquet-feeds')

    assert browser.cssselect('.teaser-small__kicker--zett-parquet')

    kicker_logo = browser.cssselect('.teaser-small__kicker--zett-parquet svg')
    assert len(kicker_logo) == 0  # no kicker logos inside zett parquet


def test_zett_parquet_should_link_to_zett(testbrowser):
    browser = testbrowser('/zeit-online/parquet-feeds')

    link_logo = browser.cssselect('.parquet-meta__title--zett')[0]
    link_more = browser.cssselect('.parquet-meta__more-link--zett')[0]

    assert link_logo.get('href') == (
        'https://ze.tt/?utm_campaign=ref&utm_content=zett_zon_parkett_teaser_x'
        '&utm_medium=fix&utm_source=zon_zettaudev_int'
        '&wt_zmc=fix.int.zettaudev.zon.ref.zett.zon_parkett.teaser.x')
    assert link_more.get('href') == (
        'https://ze.tt/?utm_campaign=ref&utm_content=zett_zon_parkett_teaser_x'
        '&utm_medium=fix&utm_source=zon_zettaudev_int'
        '&wt_zmc=fix.int.zettaudev.zon.ref.zett.zon_parkett.teaser.x')


def test_zett_parquet_should_have_ads(testbrowser):
    browser = testbrowser('/zeit-online/parquet-feeds')
    ad = browser.cssselect(
        'article[data-unique-id="https://ze.tt/wichtiges-vom-'
        'wochenende-update-32/"] .teaser-small__label')[0]

    assert ad.text == 'Anzeige'


def test_imagecopyright_tags_are_present_on_centerpages(testbrowser):
    browser = testbrowser('/zeit-online/slenderized-index')
    figures = browser.cssselect('figure *[itemprop=copyrightHolder]')
    assert len(figures) == 3


def test_imagecopyright_tags_are_not_displayed_on_centerpages(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-online/slenderized-index' % testserver.url)
    copyright = driver.find_elements_by_class_name('figcaption--hidden')
    assert copyright[0].is_displayed() is False
    assert copyright[1].is_displayed() is False
    assert copyright[2].is_displayed() is False


def test_imagecopyright_link_is_present_on_centerpages(testbrowser):
    browser = testbrowser('/zeit-online/index')
    link = browser.cssselect('.footer-links__link.js-image-copyright-footer')
    assert len(link) == 1


def test_imagecopyright_link_is_present_on_articles(testbrowser):
    browser = testbrowser('/zeit-online/article/zeit')
    link = browser.cssselect('.footer-links__link.js-image-copyright-footer')
    assert len(link) == 1


def test_imagecopyright_is_shown_on_click(selenium_driver, testserver):
    driver = selenium_driver
    driver.maximize_window()
    driver.get('%s/zeit-online/slenderized-index' % testserver.url)
    link = driver.find_element_by_css_selector('.js-image-copyright-footer')
    driver.execute_script('arguments[0].click()', link)
    try:
        WebDriverWait(driver, 5).until(
            expected_conditions.presence_of_element_located(
                (By.CLASS_NAME, 'image-copyright-footer')))
    except TimeoutException:
        assert False, 'Image Copyright in Footer not visible within 5 seconds'
    else:
        copyrights = driver.find_elements_by_css_selector(
            '.image-copyright-footer__item')
        assert len(copyrights) == 3

        linked_copyrights = driver.find_elements_by_css_selector(
            '.image-copyright-footer__item a')
        assert len(linked_copyrights) == 1

        closelink = driver.find_element_by_class_name(
            'js-image-copyright-footer-close')
        driver.execute_script('arguments[0].click()', closelink)
        try:
            WebDriverWait(driver, 5).until(
                expected_conditions.invisibility_of_element_located(
                    (By.CLASS_NAME, 'image-copyright-footer')))
        except TimeoutException:
            assert False, 'Copyright in Footer not hidden within 5 seconds'
        else:
            assert True


def test_zmo_teaser_kicker_should_contain_logo(testbrowser):
    browser = testbrowser('/zeit-online/journalistic-formats-zmo')

    teaser_fullwidth_logo = browser.cssselect(
        '.teaser-fullwidth__kicker-logo--zmo')
    teaser_classic_logo = browser.cssselect(
        '.teaser-classic__kicker-logo--zmo')
    teaser_large_logo = browser.cssselect(
        '.teaser-large__kicker-logo--zmo')
    teaser_small_logo = browser.cssselect(
        '.teaser-small__kicker-logo--zmo')
    teaser_small_minor_logo = browser.cssselect(
        '.teaser-small-minor__kicker-logo--zmo')
    teaser_kicker_zmo_parquet = browser.cssselect(
        '.teaser-small__kicker--zmo-parquet .teaser-small__kicker-logo--zmo')

    assert len(teaser_fullwidth_logo) == 1
    assert len(teaser_classic_logo) == 1
    assert len(teaser_large_logo) == 2
    assert len(teaser_small_logo) == 4
    assert len(teaser_small_minor_logo) == 2
    # assert there is no kicker logo when in zmo parquet
    assert len(teaser_kicker_zmo_parquet) == 0


def test_zmo_teaser_kicker_should_have_zmo_modifier(testbrowser):
    browser = testbrowser('/zeit-online/journalistic-formats-zmo')

    teaser_fullwidth_kicker = browser.cssselect(
        '.teaser-fullwidth__kicker--zmo')
    teaser_classic_kicker = browser.cssselect(
        '.teaser-classic__kicker--zmo')
    teaser_large_kicker = browser.cssselect(
        '.teaser-large__kicker--zmo')
    teaser_small_kicker = browser.cssselect(
        '.teaser-small__kicker--zmo')
    teaser_small_minor_kicker = browser.cssselect(
        '.teaser-small-minor__kicker--zmo')
    teaser_parquet_kicker = browser.cssselect(
        '.teaser-small__kicker--zmo-parquet.teaser-small__kicker--zmo')

    assert len(teaser_fullwidth_kicker) == 1
    assert len(teaser_classic_kicker) == 1
    assert len(teaser_large_kicker) == 2
    assert len(teaser_small_kicker) == 6
    assert len(teaser_small_minor_kicker) == 2
    assert len(teaser_parquet_kicker) == 2


def test_longform_should_not_contain_logo_in_kicker(testbrowser):
    browser = testbrowser('/zeit-online/journalistic-formats-zmo')

    major = browser.cssselect('.cp-area--major')[0]
    assert len(major.cssselect('.teaser-small ')) == 3
    assert len(major.cssselect('.teaser-small__kicker-logo--zmo')) == 2


def test_zett_teaser_kicker_should_contain_logo(testbrowser):
    browser = testbrowser('/zeit-online/journalistic-formats-zett')

    teaser_fullwidth_logo = browser.cssselect(
        '.teaser-fullwidth__kicker-logo--zett')
    teaser_classic_logo = browser.cssselect(
        '.teaser-classic__kicker-logo--zett')
    teaser_large_logo = browser.cssselect(
        '.teaser-large__kicker-logo--zett')
    teaser_small_logo = browser.cssselect(
        '.teaser-small__kicker-logo--zett')
    teaser_small_minor_logo = browser.cssselect(
        '.teaser-small-minor__kicker-logo--zett')
    teaser_square_logo = browser.cssselect(
        '.teaser-square__kicker-logo--zett')

    assert len(teaser_fullwidth_logo) == 1
    assert len(teaser_classic_logo) == 1
    assert len(teaser_large_logo) == 2
    assert len(teaser_small_logo) == 4
    assert len(teaser_small_minor_logo) == 2
    assert len(teaser_square_logo) == 2


def test_zett_teaser_kicker_should_have_zett_modifier(testbrowser, testserver):
    browser = testbrowser('/zeit-online/journalistic-formats-zett')

    teaser_fullwidth_kicker = browser.cssselect(
        '.teaser-fullwidth__kicker--zett')
    teaser_classic_kicker = browser.cssselect(
        '.teaser-classic__kicker--zett')
    teaser_large_kicker = browser.cssselect(
        '.teaser-large__kicker--zett')
    teaser_small_kicker = browser.cssselect(
        '.teaser-small__kicker--zett')
    teaser_small_minor_kicker = browser.cssselect(
        '.teaser-small-minor__kicker--zett')
    teaser_square_kicker = browser.cssselect(
        '.teaser-square__kicker--zett')

    assert len(teaser_fullwidth_kicker) == 1
    assert len(teaser_classic_kicker) == 1
    assert len(teaser_large_kicker) == 2
    assert len(teaser_small_kicker) == 4
    assert len(teaser_small_minor_kicker) == 2
    assert len(teaser_square_kicker) == 2


def test_zett_teaser_should_contain_campaign_parameter(testbrowser):
    browser = testbrowser('/zeit-online/journalistic-formats-zett')
    select = browser.cssselect
    links = select('.cp-area:not(.cp-area--zett) a[href*="//ze.tt"]')
    zett_parquet_links = select('.cp-area--zett a[href*="//ze.tt"]')

    assert len(links)
    assert len(zett_parquet_links)

    for link in links:
        assert ('?utm_campaign=ref&utm_content=zett_zon_teaser_teaser_x'
                '&utm_medium=fix&utm_source=zon_zettaudev_int'
                '&wt_zmc=fix.int.zettaudev.zon.ref.zett.zon_teaser.teaser.x'
                ) in link.get('href')

    for link in zett_parquet_links:
        assert ('?utm_campaign=ref&utm_content=zett_zon_parkett_teaser_x'
                '&utm_medium=fix&utm_source=zon_zettaudev_int'
                '&wt_zmc=fix.int.zettaudev.zon.ref.zett.zon_parkett.teaser.x'
                ) in link.get('href')


def test_printkiosk_is_structured_correctly(testbrowser):
    browser = testbrowser('/angebote/printkiosk/vorschau')
    teasers = browser.cssselect('.cp-area--printkiosk .teaser-printkiosk')
    assert len(teasers) == 4
    paginationbutton = browser.cssselect('.js-bar-teaser-paginate')
    assert len(paginationbutton) == 1
    assert paginationbutton[0].get('data-sourceurl').endswith('?p=')


def test_printkiosk_displays_items_according_to_breakpoint(
        selenium_driver, testserver, screen_size):
    driver = selenium_driver
    driver.set_window_size(screen_size[0], screen_size[1])
    driver.get('%s/angebote/printkiosk/vorschau' % testserver.url)
    teasers = driver.find_elements_by_class_name('teaser-printkiosk')

    if screen_size[0] == 320:
        assert teasers[0].is_displayed() is True
        assert teasers[1].is_displayed() is False
        assert teasers[2].is_displayed() is False
        assert teasers[3].is_displayed() is False
    if screen_size[0] == 520:
        assert teasers[0].is_displayed() is True
        assert teasers[1].is_displayed() is True
        assert teasers[2].is_displayed() is False
        assert teasers[3].is_displayed() is False
    if screen_size[0] == 768:
        assert teasers[0].is_displayed() is True
        assert teasers[1].is_displayed() is True
        assert teasers[2].is_displayed() is True
        assert teasers[3].is_displayed() is False
    if screen_size[0] == 1000:
        assert teasers[0].is_displayed() is True
        assert teasers[1].is_displayed() is True
        assert teasers[2].is_displayed() is True
        assert teasers[3].is_displayed() is True


def test_printkiosk_area_should_render_in_isolation_firstpage(testbrowser):
    browser = testbrowser(
        '/angebote/printkiosk/vorschau/area/'
        'id-f103fa99-95e2-4094-8bb9-d56b482325f7')
    teasers = browser.cssselect('.cp-area--printkiosk .teaser-printkiosk')
    assert len(teasers) == 4
    teasertexts = browser.cssselect('.teaser-printkiosk__title')
    teasertexts[0].text = 'DIE ZEIT'


def test_printkiosk_area_should_render_in_isolation_secondpage(testbrowser):
    browser = testbrowser(
        '/angebote/printkiosk/vorschau/area/'
        'id-f103fa99-95e2-4094-8bb9-d56b482325f7?p='
        'http://xml.zeit.de/angebote/printkiosk/linkobjekte/zeit-spezial')
    teasers = browser.cssselect('.cp-area--printkiosk .teaser-printkiosk')
    assert len(teasers) == 4
    teasertexts = browser.cssselect('.teaser-printkiosk__title')
    assert teasertexts[0].text == 'ZEIT GESCHICHTE'


def test_printkiosk_area_should_render_in_isolation_skippage(testbrowser):
    browser = testbrowser(
        '/angebote/printkiosk/vorschau/area/'
        'id-f103fa99-95e2-4094-8bb9-d56b482325f7?p='
        'http://xml.zeit.de/angebote/printkiosk/linkobjekte/zeit-spezial')
    teasers = browser.cssselect('.cp-area--printkiosk .teaser-printkiosk')
    assert len(teasers) == 4
    teasertexts = browser.cssselect('.teaser-printkiosk__title')
    assert teasertexts[0].text == 'ZEIT GESCHICHTE'
    assert teasertexts[2].text == 'DIE ZEIT'


def test_printkiosk_loads_next_page_on_click(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('{}/angebote/printkiosk/vorschau'.format(testserver.url))
    driver.set_window_size(1200, 860)
    teaserbutton = driver.find_element_by_css_selector(
        '.js-bar-teaser-paginate')
    teaserbutton.click()

    condition = expected_conditions.text_to_be_present_in_element((
        By.CSS_SELECTOR, '.teaser-printkiosk__title'),
        'ZEIT GESCHICHTE')
    assert WebDriverWait(driver, 5).until(condition), (
        'New teasers not loaded within 5 seconds')

    new_teaser_titles = driver.find_elements_by_css_selector(
        '.teaser-printkiosk__title')
    assert new_teaser_titles[0].text == 'ZEIT GESCHICHTE'
    assert new_teaser_titles[2].text == 'DIE ZEIT'


def test_centerpage_page_should_be_reconstructed(application, dummy_request):
    dummy_request.GET['p'] = '3'
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{'uniqueId': 'http://zeit.de/%s' % i} for i in range(35)]
    cp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/dynamic/umbrien')
    view = zeit.web.site.view_centerpage.CenterpagePage(cp, dummy_request)
    assert len(view.regions) == 2
    assert view.regions[0].values()[0].values()[0].supertitle == 'Griechenland'
    assert view.regions[1].values()[0].kind == 'ranking'


def test_centerpage_page_should_reconstruct_multiple_modules(
        application, dummy_request):
    dummy_request.GET['p'] = '2'
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{'uniqueId': 'http://zeit.de/%s' % i} for i in range(15)]
    cp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/dynamic/umbrien')
    mod = cp.body.values()[0].values()[0].create_item('cpextra')
    mod.cpextra = 'search-form'
    view = zeit.web.site.view_centerpage.CenterpagePage(cp, dummy_request)
    assert len(view.regions) == 2
    assert view.regions[0].values()[0].values()[0].supertitle == 'Griechenland'
    assert isinstance(
        view.regions[0].values()[0].values()[1],
        zeit.web.site.module.search_form.Form)


def test_centerpage_page_should_reconstruct_multiple_areas(
        application, dummy_request):
    dummy_request.GET['p'] = '3'
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{'uniqueId': 'http://zeit.de/%s' % i} for i in range(35)]
    cp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/dynamic/umbrien')
    area = cp.body.values()[0].create_item('area', 1)
    mod = area.create_item('cpextra')
    mod.cpextra = 'search-form'
    view = zeit.web.site.view_centerpage.CenterpagePage(cp, dummy_request)
    assert len(view.regions) == 2
    assert view.regions[0].values()[0].values()[0].supertitle == 'Griechenland'
    assert isinstance(
        view.regions[0].values()[1].values()[0],
        zeit.web.site.module.search_form.Form)


def test_centerpage_page_should_require_ranking(application, dummy_request):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/slenderized-index')
    view = zeit.web.site.view_centerpage.CenterpagePage(cp, dummy_request)
    with pytest.raises(pyramid.httpexceptions.HTTPNotFound):
        list(view.regions)


def test_centerpage_page_integration(testbrowser, data_solr):
    browser = testbrowser('/dynamic/umbrien?p=2')
    # Curated content is not shown
    assert 'Ich bin nicht intellektuell' not in browser.contents
    # Header is kept
    assert 'Das linke Experiment' in browser.contents
    # Ranking is kept
    assert 'cp-area--ranking' in browser.contents


def test_ranking_ara_should_offset_resultset_on_materialized_cp(
        application, dummy_request):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{'uniqueId': 'http://zeit.de/%s' % i} for i in range(35)]
    cp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/dynamic/umbrien')
    context = zeit.web.core.utils.find_block(cp, attrib='area', kind='ranking')
    dummy_request.GET['p'] = 2
    area = zeit.web.core.centerpage.get_area(context)
    assert len(area.values()) == 10
    assert area.total_pages == 5
    assert area._content_query.filter_query == (
        'NOT (uniqueId:"http://xml.zeit.de/zeit-magazin/mode-design/2014-05'
        '/karl-lagerfeld-interview" OR uniqueId:"http://xml.zeit.de'
        '/zeit-magazin/leben/2015-02/magdalena-ruecken-fs")')


def test_ranking_area_should_not_offset_resultset_on_materialized_cp(
        application, dummy_request):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{'uniqueId': 'http://zeit.de/%s' % i} for i in range(35)]
    cp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/dynamic/ukraine')
    context = zeit.web.core.utils.find_block(cp, attrib='area', kind='ranking')
    area = zeit.web.core.centerpage.get_area(context)
    assert len(area.values()) == 10
    assert area.total_pages == 4
    assert area._content_query.filter_query == '*:*'


@pytest.mark.parametrize('params, page', ([{'p': '2'}, 2], [{}, 1]))
def test_ranking_area_should_handle_various_page_values(
        params, page, application, dummy_request):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{'uniqueId': 'http://zeit.de/%s' % i} for i in range(12)]
    cp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/dynamic/ukraine')
    context = zeit.web.core.utils.find_block(cp, attrib='area', kind='ranking')
    dummy_request.GET = params
    area = zeit.web.core.centerpage.get_area(context)
    assert area.page == page


def test_ranking_area_should_silently_accept_emptyness(
        application, dummy_request):
    cp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/suche/index')
    context = zeit.web.core.utils.find_block(cp, attrib='area', kind='ranking')
    area = zeit.web.core.centerpage.get_area(context)
    assert area.pagination == []


def test_ranking_area_should_be_found_regardless_of_kind(
        application, dummy_request):
    cp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/dynamic/umbrien')
    cp.body.values()[1].values()[0].kind = 'author-list'
    view = zeit.web.site.view_centerpage.CenterpagePage(cp, dummy_request)
    assert view.area_providing_pagination


def test_no_author_should_not_display_byline(testbrowser, workingcopy):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/cp-content/article-01')
    with checked_out(article) as co:
        co.authorships = ()

    browser = testbrowser('/zeit-online/slenderized-centerpage')
    teaser = browser.cssselect(
        '.teaser-fullwidth[data-unique-id="{}"] '.format(article.uniqueId))[0]

    assert not teaser.cssselect('.teaser-fullwidth__byline')


def test_shop_and_printkiosk_must_not_contain_links_inside_links(testbrowser):
    browser = testbrowser('/angebote/zeit-shop-buehne/vorschau')
    assert len(browser.cssselect('.teaser-shop:first-child a')) == 1

    browser = testbrowser('/angebote/printkiosk/vorschau')
    assert len(browser.cssselect('.teaser-printkiosk:first-child a')) == 1


def test_shop_contains_load_more_button(testbrowser):
    browser = testbrowser('/angebote/zeit-shop-buehne/vorschau')
    assert browser.cssselect('.cp-area--shop .js-bar-teaser-paginate')


def test_dynamic_cps_detect_videos_of_type_video(
        application, dummy_request):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{'uniqueId':
                     'http://xml.zeit.de/video/2014-01/1953013471001',
                     'type': 'video'}]

    cp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/dynamic/ukraine')

    context = zeit.web.core.utils.find_block(cp, attrib='area', kind='ranking')
    area = zeit.web.core.centerpage.get_area(context)
    teaser = area.values()[0]
    video = list(teaser)[0]

    assert zeit.web.core.template.is_video(video)


def test_dynamic_cps_show_detect_videos_with_ivideo_interface(
        application, dummy_request):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{'uniqueId':
                     'http://xml.zeit.de/video/2014-01/1953013471001',
                     'type': 'zeit.brightcove.interfaces.IVideo'}]

    cp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/dynamic/ukraine')

    context = zeit.web.core.utils.find_block(cp, attrib='area', kind='ranking')
    area = zeit.web.core.centerpage.get_area(context)
    teaser = area.values()[0]
    video = list(teaser)[0]

    assert zeit.web.core.template.is_video(video)


def test_teaser_classic_should_not_have_gradient_overlay(testbrowser):
    browser = testbrowser('/zeit-online/classic-teaser')
    assert len(browser.cssselect('a.teaser-fullwidth__media-link')) == 0


def test_headerimage_has_appropriate_html_structure(testbrowser):
    browser = testbrowser('/zeit-online/index-with-image')
    image = browser.cssselect('.header-image__media-item')[0]
    assert image.get('data-ratio') == '3.5'  # varian=panorama
    assert image.get('data-mobile-ratio') == '2.33333333333'  # variant=cinema


def test_dynamic_page_has_correct_structure(testbrowser):
    select = testbrowser('/serie/alpha-centauri').cssselect
    title = select('head title')[0]
    headline = select('.header-image h1')[0]

    assert len(select('.cp-region--solo')) == 2
    assert len(select('.cp-area--solo')) == 1
    assert len(select('.cp-area--ranking')) == 1
    assert len(select('.header-image.header-image--overlain')) == 1
    assert title.text.startswith('Serie alpha-Centauri')
    assert headline.text_content().strip() == 'Serie: alpha-Centauri'


def test_headerimage_is_overlain_on_dynamic_page(testbrowser):
    browser = testbrowser('/serie/alpha-centauri')
    module = browser.cssselect('.header-image')[0]
    assert 'header-image--overlain' in module.get('class')


def test_headerimage_is_overlain_on_materialized_simple_page(testbrowser):
    browser = testbrowser('/serie/tontraeger')
    module = browser.cssselect('.header-image')[0]
    assert 'header-image--overlain' in module.get('class')


def test_headerimage_is_overlain_on_materialized_page_with_markdown(
        testbrowser):
    browser = testbrowser('/serie/app-kritik')
    module = browser.cssselect('.header-image')[0]
    assert 'header-image--overlain' in module.get('class')


def test_headerimage_is_not_overlain_on_materialized_curated_page(testbrowser):
    browser = testbrowser('/serie/70-jahre-zeit')
    module = browser.cssselect('.header-image')[0]
    assert 'header-image--overlain' not in module.get('class')


def test_headerimage_is_overlain_on_materialized_following_page(testbrowser):
    browser = testbrowser('/serie/70-jahre-zeit?p=2')
    module = browser.cssselect('.header-image')[0]
    assert 'header-image--overlain' in module.get('class')


def test_zco_parquet_has_zco_styles(testbrowser):
    browser = testbrowser('/zeit-online/centerpage/teasers-to-campus')
    select = browser.cssselect

    assert len(select('.cp-area--zco-parquet')) == 1
    assert len(select('.parquet-meta__more-link--zco')) == 1
    assert len(select('.parquet-meta__title--zco')) == 1
    assert len(select('.parquet-meta__logo--zco')) == 1

    assert len(select(
        '[class^="teaser"][class*="__kicker--zco-parquet"]')) == 2


def test_author_list_should_show_authors(testbrowser):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{'uniqueId': 'http://xml.zeit.de/autoren/j_random'}]
    browser = testbrowser('/autoren/register_A')
    assert len(browser.cssselect('.author-list__item')) == 1


def test_centerpage_contains_webtrekk_parameter_asset(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set('third_party_modules')
    browser = testbrowser('/zeit-online/centerpage/cardstack')
    script = browser.cssselect(
        'script[src*="/static/js/webtrekk/webtrekk"] + script')[0]

    assert '27: "cardstack.1.2.4;quiz.2.2.2"' in script.text_content().strip()


def test_comment_count_in_teaser_not_shown_when_comments_disabled(
        testbrowser, workingcopy):
    id = 'http://xml.zeit.de/zeit-online/article/01'
    article = zeit.cms.interfaces.ICMSContent(id)
    with zeit.cms.checkout.helper.checked_out(article) as co:
        co.commentSectionEnable = False
    with mock.patch(
            'zeit.web.core.comments.Community.get_comment_counts') as counts:
        counts.return_value = {id: 35}
        browser = testbrowser('/zeit-online/classic-teaser')
    assert not browser.cssselect(
        'article[data-unique-id="{}"] .teaser-small__commentcount'.format(id))


def test_teaser_link_title_should_match_kicker_and_headline(testbrowser):
    browser = testbrowser('/zeit-online/slenderized-index')
    articles = browser.cssselect('article')
    for article in articles:
        links = article.cssselect('a:not([itemprop="url"])')
        assert links[0].get('title') == links[1].get('title')


def test_dynamic_cps_should_consider_teaser_image_fill_color(testbrowser):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{
        'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/01',
        'image-base-id': [(u'http://xml.zeit.de/zeit-magazin/images/'
                           'harald-martenstein-wideformat')],
        'image-fill-color': [u'A3E6BB'], 'teaserText': 'text',
        'teaserSupertitle': 'supertitle', 'teaserTitle': 'title',
        'date_first_released': '2012-02-22T14:36:32.452398+00:00'}, {
            'uniqueId': 'http://xml.zeit.de/zeit-magazin/article/02',
            'image-base-id': [(u'http://xml.zeit.de/zeit-magazin/images/'
                               'harald-martenstein-wideformat')],
            'image-fill-color': [u''], 'teaserText': 'text',
            'teaserSupertitle': 'supertitle', 'teaserTitle': 'title',
            'date_first_released': '2012-02-22T14:36:32.452398+00:00'}]

    browser = testbrowser('/serie/martenstein')
    image1 = browser.cssselect('.cp-area--ranking article img')[0]
    image2 = browser.cssselect('.cp-area--ranking article img')[1]

    assert image1.get('data-src').endswith('__A3E6BB')
    assert not image2.get('data-src').endswith('__')


def test_dynamic_cps_should_use_actual_fill_color_if_exposed_anyway(
        testbrowser):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = [{
        'uniqueId': ('http://xml.zeit.de/zeit-online/article'
                     '/podcast-header-serie'),
        'teaserText': 'text',
        'teaserSupertitle': 'supertitle', 'teaserTitle': 'title',
        'date_first_released': '2012-02-22T14:36:32.452398+00:00'}]

    browser = testbrowser('/serie/app-kritik')
    image = browser.cssselect('.cp-area--ranking article img')[0]
    assert image.get('data-src').endswith('__EEB200')


def test_dossier_teaser_should_be_rendered(testbrowser):
    browser = testbrowser('/zeit-online/dossier-teaser')
    teaser = browser.cssselect('.cp-area.cp-area--solo .teaser-dossier')

    assert teaser


def test_dossier_teaser_image_should_have_attributes_for_mobile_variant(
        testbrowser):
    browser = testbrowser('/zeit-online/dossier-teaser')
    img = browser.cssselect('.teaser-dossier__media-item')[0]
    assert img.get('data-mobile-ratio').startswith('1.77')
    assert 'image/crystal-meth-nancy-schmidt/wide' in img.get(
        'data-mobile-src')


def test_dossier_teaser_image_should_use_mobile_variant_on_mobile(
        selenium_driver, testserver):
    driver = selenium_driver

    driver.set_window_size(screen_sizes[1][0], screen_sizes[1][1])
    driver.get('%s/zeit-online/dossier-teaser' % testserver.url)
    img = driver.find_element_by_class_name('teaser-dossier__media-item')
    ratio = float(img.size['width']) / img.size['height']
    assert '/wide__' in img.get_attribute('src'), \
        'wide image variant should be used on mobile devices'
    assert 1.7 < ratio < 1.8, 'mobile ratio should be 16:9-ish'


def test_dossier_teaser_has_correct_width_in_all_screen_sizes(
        selenium_driver, testserver, screen_size):
    driver = selenium_driver
    driver.set_window_size(screen_size[0], screen_size[1])
    driver.get('%s/zeit-online/dossier-teaser' % testserver.url)
    teaser = driver.find_element_by_class_name('teaser-dossier')
    helper = driver.find_element_by_class_name('teaser-dossier__container')

    assert teaser.is_displayed(), 'dossier teaser missing'
    assert helper.is_displayed(), 'dossier teaser container missing'

    if screen_size[0] == 768:
        width = teaser.size.get('width')
        assert int(helper.size.get('width')) == int(width * 0.72)

    elif screen_size[0] == 1000:
        width = teaser.size.get('width')
        assert int(helper.size.get('width')) == int(round(width * 0.6666))


def test_cp_teaser_should_display_three_authors_max(testbrowser):
    browser = testbrowser('/zeit-online/slenderized-index')
    byline_raw = browser.cssselect('.teaser-small__byline')
    byline = ' '.join(byline_raw[0].text.strip().split())
    assert byline == 'Eine Glosse von Wenke Husmann,' \
                     ' Jochen Bittner, Heike Jahberg u.a.'


def test_imagecopyright_includes_videostage_poster_copyright(testbrowser):
    browser = testbrowser('/zeit-online/video-stage')
    figures = browser.cssselect('figure *[itemprop=copyrightHolder]')
    # robot video on stage has no copyright - on purpose.
    assert len(figures) == 4


def test_volume_centerpage_has_volume_navigation(testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.site.view_centerpage.Centerpage,
                        'volume_next',
                        {'link': 'http://ww.zeit.de/2016/02/index',
                         'label': '02/2016'})
    monkeypatch.setattr(zeit.web.site.view_centerpage.Centerpage,
                        'volume_previous',
                        {'link': 'http://ww.zeit.de/2015/52/index',
                         'label': '52/2015'})
    browser = testbrowser('/2016/01/index')
    nav = browser.cssselect('.teaser-volumeteaser')
    assert len(nav) == 1

    current = nav[0].cssselect('.teaser-volumeteaser__current')
    prev = nav[0].cssselect('.teaser-volumeteaser__previous-link')
    next = nav[0].cssselect('.teaser-volumeteaser__next-link')
    modifier = browser.cssselect('.teaser-volumeteaser--below-volumeheader')

    assert len(current) == 1
    assert len(prev) == 1
    assert len(next) == 1
    assert len(modifier) == 1
    assert '2015/52' in prev[0].get('href')
    assert '52/2015' in prev[0].text.strip()
    assert '2016/02' in next[0].get('href')
    assert '02/2016' in next[0].text.strip()

    packshot = current[0].cssselect('.teaser-volumeteaser__packshot')
    cta = current[0].cssselect('.teaser-volumeteaser__cta')
    media = current[0].cssselect('.teaser-volumeteaser__media')

    assert len(packshot) == 1
    assert len(cta) == 1
    assert len(media) == 1


def test_volume_centerpage_volume_fallback_for_missing_packshot(testbrowser):
    browser = testbrowser('/2016/02/index')
    packshot = browser.cssselect('.teaser-volumeteaser__packshot noscript')
    assert 'default_packshot_diezeit' in packshot[0].get('data-src')


def test_volume_centerpage_navi_dont_show_invalid_links(testbrowser):
    browser = testbrowser('/2016/02/index')

    next = browser.cssselect('.teaser-volumeteaser__next-link')
    prev = browser.cssselect('.teaser-volumeteaser__previous-link')
    assert len(next) == 0
    assert len(prev) == 0


def test_volume_centerpage_has_volume_header(testbrowser):
    browser = testbrowser('/2016/01/index')

    volume_header = browser.cssselect('.cp-area--volume-header')
    teaser = volume_header[0].cssselect('.volume-heading-teaser')

    caption = volume_header[0].cssselect('.volume-heading__caption')

    assert len(volume_header) == 1
    assert 'Ausgabe Nr. 01/2016' in caption[0].text.strip()
    assert len(teaser) == 3


def test_volume_overview_has_adapted_centerpage_header(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/2016/index' % testserver.url)
    header = driver.find_element_by_css_selector(
        '.centerpage-header--archive')
    text = driver.find_element_by_css_selector(
        '.centerpage-header__text')
    title = driver.find_element_by_css_selector(
        '.centerpage-header__title')
    dropdown = driver.find_element_by_css_selector(
        '.centerpage-header__dropdown')
    link = driver.find_element_by_css_selector(
        '.centerpage-header__link')
    dropdown.find_element_by_xpath("//option[text()='1947']").click()

    assert header.is_displayed()
    assert dropdown.is_displayed()
    assert link.is_displayed()
    assert 'DIE ZEIT aus dem Jahr 2016' in text.text
    assert 'Jahrgang 2016' in title.text
    assert '1947/index' in link.get_attribute('href')


def test_volume_overview_teasers_render_expected_markup(testbrowser):
    browser = testbrowser('/2016/index')
    teasers = browser.cssselect(
        '.cp-area--volume-overview .teaser-volume-overview a')
    assert len(teasers) == 7
    for teaser in teasers:
        caption = teaser.cssselect('.teaser-volume-overview__cta')[0]
        caption_text = caption.text_content().strip()
        assert caption_text.startswith('Jetzt Ausgabe ')
        assert caption_text.endswith(' lesen')
        assert 'teaser-volume-overview__media' in \
               teaser.cssselect('figure')[0].get('class')


def test_zplus_teaser_has_zplus_badge(testbrowser):
    browser = testbrowser('/zeit-online/centerpage/zplus')

    # test fullwidth teasers
    teasers = browser.cssselect('.cp-area--solo article')
    assert len(teasers) == 3
    for teaser in teasers:
        layout = teaser.get('class').split()[0]
        assert teaser.cssselect('.{}__kicker-logo--zplus'.format(layout))

    # test major area teasers
    teasers = browser.cssselect('.cp-area--major article')
    assert len(teasers) == 6
    for teaser in teasers:
        layout = teaser.get('class').split()[0]
        assert teaser.cssselect('.{}__kicker-logo--zplus'.format(layout))

    # test minor area teasers
    teasers = browser.cssselect('.cp-area--minor article[data-zplus]')
    assert len(teasers) == 7
    for teaser in teasers:
        layout = teaser.get('class').split()[0]
        assert (teaser.cssselect('.{}__kicker-logo--zplus'.format(layout)) or
                teaser.cssselect(
                    '.{}__kicker-logo--zplus-register'.format(layout)))

    # test square teasers
    teasers = browser.cssselect('.cp-area--duo article[data-zplus]')
    assert len(teasers) == 3
    for teaser in teasers:
        layout = teaser.get('class').split()[0]
        assert teaser.cssselect('.{}__kicker-logo--zplus'.format(layout))

    # test parquet teasers
    teasers = browser.cssselect('.cp-area--parquet article')
    assert len(teasers) == 6
    for teaser in teasers:
        layout = teaser.get('class').split()[0]
        assert teaser.cssselect('.{}__kicker-logo--zplus'.format(layout))

    # test ZMO parquet teasers
    teasers = browser.cssselect('.cp-area--zmo-parquet article')
    assert len(teasers) == 3
    for teaser in teasers:
        assert teaser.cssselect('.teaser-small__kicker-logo--zplus')


def test_zplus_teaser_should_force_mobile_images(testbrowser):
    browser = testbrowser('/zeit-online/centerpage/zplus')
    figures = browser.cssselect('figure.teaser-small__media, '
                                'figure.teaser-small-minor__media')

    assert figures
    for figure in figures:
        assert '__media--force-mobile' in figure.get('class')


def test_register_teaser_has_zplus_register_badge(testbrowser):
    browser = testbrowser('/zeit-online/centerpage/register')

    # test fullwidth teasers
    teasers = browser.cssselect('.cp-area--solo article')
    assert len(teasers) == 3
    for teaser in teasers:
        layout = teaser.get('class').split()[0]
        assert teaser.cssselect(
            '.{}__kicker-logo--zplus-register'.format(layout))

    # test major area teasers
    teasers = browser.cssselect('.cp-area--major article')
    assert len(teasers) == 6
    for teaser in teasers:
        layout = teaser.get('class').split()[0]
        assert teaser.cssselect(
            '.{}__kicker-logo--zplus-register'.format(layout))

    # test minor area teasers
    teasers = browser.cssselect(
        '.cp-area--minor article[data-zplus$="register"]')
    assert len(teasers) == 5
    for teaser in teasers:
        layout = teaser.get('class').split()[0]
        assert teaser.cssselect(
            '.{}__kicker-logo--zplus-register'.format(layout))

    # test square teasers
    teasers = browser.cssselect('.cp-area--duo article[data-zplus]')
    assert len(teasers) == 3
    for teaser in teasers:
        layout = teaser.get('class').split()[0]
        assert teaser.cssselect(
            '.{}__kicker-logo--zplus-register'.format(layout))

    # test parquet teasers
    teasers = browser.cssselect('.cp-area--parquet article')
    assert len(teasers) == 6
    for teaser in teasers:
        layout = teaser.get('class').split()[0]
        assert teaser.cssselect(
            '.{}__kicker-logo--zplus-register'.format(layout))

    # test ZMO parquet teasers
    teasers = browser.cssselect('.cp-area--zmo-parquet article')
    assert len(teasers) == 1
    for teaser in teasers:
        assert teaser.cssselect('.teaser-small__kicker-logo--zplus-register')


def test_zplus_teaser_has_no_badge_in_ressort_area(testbrowser, data_solr):
    browser = testbrowser('/zeit-online/centerpage/print-ressort')
    teaser = browser.cssselect(
        '.cp-region--solo:nth-child(3) article.teaser-large')[0]
    assert not teaser.cssselect('.teaser-large__kicker-logo--zplus')


def test_campus_teaser_has_no_badge_in_ressort_area(testbrowser, data_solr):
    browser = testbrowser('/zeit-online/centerpage/print-ressort-with-campus')
    assert not browser.cssselect('.teaser-small__kicker-logo--zco')
    assert not browser.cssselect('.teaser-large__kicker-logo--zco')


def test_ressort_areas_have_ressort_title(testbrowser, data_solr):
    browser = testbrowser('/zeit-online/centerpage/print-ressort')
    areas = browser.cssselect('.cp-area--print-ressort')
    assert areas[0].cssselect('.cp-area__headline')[0].text == 'Politik'
    assert areas[1].cssselect('.cp-area__headline')[0].text == 'Wirtschaft'


def test_ressort_areas_should_disintegrate(testbrowser):
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    solr.results = []
    browser = testbrowser('/zeit-online/centerpage/print-ressort')
    assert len(browser.cssselect('.cp-area--print-ressort')) == 0


def test_exclusive_areas_render_correctly(testbrowser):
    browser = testbrowser('/zeit-online/centerpage/exclusive')
    areas = browser.cssselect('.cp-area--exclusive-ressort')
    teasers = browser.cssselect('.cp-area--exclusive-ressort article')
    assert areas[0].cssselect('.cp-area__headline')[0].text == 'Politik'
    assert not areas[1].cssselect('.cp-area__headline')
    assert 'teaser-small--exclusive' in teasers[0].get('class')


def test_headerimage_should_overlay_onto_tube_area(testbrowser):
    browser = testbrowser('/zeit-online/centerpage/tube')
    assert browser.cssselect('.cp-area--tube')
    header_image = browser.cssselect('.cp-area--solo .header-image')[0]
    assert '--overlain' in header_image.get('class')


def test_volume_teaser_on_cp_has_correct_elements(testbrowser):
    browser = testbrowser('/zeit-online/centerpage/volumeteaser')

    assert len(browser.cssselect('.teaser-volumeteaser')) == 2

    teaser_linktexts = browser.cssselect('.teaser-volumeteaser__link')
    assert teaser_linktexts[0].text.strip() == (
        'Alternativtext am Teaser: Lesen Sie diese Ausgabe.')
    assert teaser_linktexts[1].text.strip() == (
        'Lesen Sie diese Ausgabe als E-Paper, App und auf dem E-Reader.')

    teaser_images = browser.cssselect('.teaser-volumeteaser__media-item')
    assert teaser_images[0].get('src').endswith(
        '/2016-09/test-printcover/original')
    assert teaser_images[1].get('src').endswith(
        '/ausgabe/default_packshot_diezeit/original')


@pytest.mark.parametrize('c1_parameter', [
    '?C1-Meter-Status=paywall&C1-Meter-User-Status=anonymous',
    '?C1-Meter-Status=paywall&C1-Meter-User-Status=registered',
    '?C1-Meter-Status=always_paid'])
def test_paywall_switch_on_volume_cp_and_show_redirect(
        testserver, c1_parameter):
    resp = requests.get(
        '{}/2015/52/index{}'.format(
            testserver.url, c1_parameter), allow_redirects=False)
    assert resp.headers['location'] == 'http://redirect.example.com'
    assert resp.status_code == 307


def test_volume_cp_should_send_correct_headers(testserver, monkeypatch):

    def next_volume(me):
        return None
    monkeypatch.setattr(
        zeit.content.volume.volume.Volume, 'next', None)
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/2015/52/index')
    request = pyramid.testing.DummyRequest()
    c1_mixin = zeit.web.core.paywall.CeleraOneMixin()
    c1_mixin.context = cp
    c1_mixin.request = request
    assert c1_mixin._c1_entitlement == 'paid'


def test_volume_overview_has_correct_pagination(testbrowser):
    browser = testbrowser('/2015/index')

    prev_tag = browser.cssselect('head link[rel="prev"]')[0]
    next_tag = browser.cssselect('head link[rel="next"]')[0]
    current_tag = browser.cssselect('head link[rel="canonical"]')[0]
    assert prev_tag.get('href').endswith('/2016/index')
    assert next_tag.get('href').endswith('/2014/index')
    assert current_tag.get('href').endswith('/2015/index')

    next_button = browser.cssselect('.pager__button--next')[0]
    assert next_button.text == 'Vorheriges Jahr'

    current_year = datetime.datetime.today().year
    prev_link = browser.cssselect('.pager__pages a')[0]
    assert prev_link.get('href').endswith('/{}/index'.format(current_year))

    current = browser.cssselect('.pager__pages .pager__page--current')[0]
    assert current.text_content() == '2015'

    meta_robots = browser.cssselect('head meta[name="robots"]')[0]
    meta_robots.get('content') == 'index,follow,noarchive'


def test_hpoverlay_settings_toggles_html_output(testbrowser):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)

    conf['hp_overlay_active'] = True
    browser = testbrowser('/zeit-online/slenderized-index')
    assert browser.cssselect('#overlay-wrapper')

    conf['hp_overlay_active'] = False
    browser = testbrowser('/zeit-online/slenderized-index')
    assert not browser.cssselect('#overlay-wrapper')


def test_hpoverlay_html_output_is_not_on_articles(testbrowser):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    conf['hp_overlay_active'] = True
    browser = testbrowser('/zeit-online/article/simple')
    assert not browser.cssselect('#overlay-wrapper')


def test_d17_icon_feature_toggle_is_working(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.unset('tag_logos')
    browser = testbrowser('/zeit-online/centerpage/taglogo')
    assert not browser.cssselect('*[data-taglogo="true"]')


def test_d17_icon_is_displayed_on_teaser(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set(
        'tag_logos', 'reader_revenue')
    browser = testbrowser('/zeit-online/centerpage/taglogo')
    assert browser.cssselect('*[data-taglogo="true"]')
    assert len(browser.cssselect('.teaser-fullwidth__kicker-logo--tag')) == 1
    assert len(browser.cssselect('.teaser-small__kicker-logo--tag')) == 4
    assert len(browser.cssselect(
        '.teaser-fullwidth-column__kicker-logo--tag')) == 1
    assert len(browser.cssselect(
        '.teaser-small-column__kicker-logo--tag')) == 1
    assert browser.cssselect(
        '.teaser-small__kicker-logo--tag + .teaser-small__kicker-logo--zco')
    text = 'Freier Teaser Kicker'
    uid = 'http://xml.zeit.de/zeit-online/cp-content/taglogo/link-d17-tag'
    attr = 'data-unique-id="{}"'.format(uid)
    selector = 'article[{}] .teaser-small__kicker-logo--tag'.format(attr)
    assert text in browser.cssselect(selector)[0].getparent().text_content()


def test_d17_icon_is_not_display_on_zplus_teaser(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set(
        'tag_logos', 'reader_revenue')
    browser = testbrowser('/zeit-online/centerpage/taglogo')
    assert not browser.cssselect(
        'teaser-small__kicker-logo--zplus + .teaser-small__kicker-logo--tag')
    assert not browser.cssselect(
        '.teaser-small__kicker-logo--tag + .teaser-small__kicker-logo--zplus')


def test_d17_icon_is_not_display_on_zmo_teaser(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set(
        'tag_logos', 'reader_revenue')
    browser = testbrowser('/zeit-online/centerpage/taglogo')
    assert not browser.cssselect(
        'teaser-small__kicker-logo--zmo + .teaser-small__kicker-logo--tag')
    assert not browser.cssselect(
        '.teaser-small__kicker-logo--tag + .teaser-small__kicker-logo--zmo')


def test_d17_icon_is_not_display_on_d17_teaser(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set(
        'tag_logos', 'reader_revenue')
    browser = testbrowser('/zeit-online/parquet')
    assert not browser.cssselect(
        '.cp-area--d17-parquet .teaser-large__kicker-logo--tag')


def test_d17_icon_is_display_on_auto_area(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set(
        'tag_logos', 'reader_revenue')
    browser = testbrowser('/zeit-online/centerpage/taglogo')
    query = ('.cp-region--solo + .cp-region--duo article:first-child '
             '.teaser-small__kicker-logo--tag')
    assert browser.cssselect(query)


def test_d17_icon_is_display_on_nextread(testbrowser):
    browser = testbrowser('/zeit-online/article/simple-nextread-taglogo')
    assert browser.cssselect('article.nextread .nextread__kicker-logo--tag')


def test_d18_icon_feature_toggle_is_working(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.unset('tag_logos')
    browser = testbrowser('/zeit-online/centerpage/taglogo-d18')
    assert not browser.cssselect('*[data-taglogo="true"]')


def test_d18_icon_is_displayed_on_teaser(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set(
        'tag_logos', 'reader_revenue')
    browser = testbrowser('/zeit-online/centerpage/taglogo-d18')
    assert browser.cssselect('*[data-taglogo="true"]')
    assert len(browser.cssselect('.teaser-fullwidth__kicker-logo--tag')) == 1
    assert len(browser.cssselect('.teaser-small__kicker-logo--tag')) == 3
    assert len(browser.cssselect(
        '.teaser-fullwidth-column__kicker-logo--tag')) == 1
    assert len(browser.cssselect(
        '.teaser-small-column__kicker-logo--tag')) == 1
    assert browser.cssselect(
        '.teaser-small__kicker-logo--tag')
    text = 'Freier Teaser Kicker'
    uid = 'http://xml.zeit.de/zeit-online/cp-content/taglogo/link-d18-tag'
    attr = 'data-unique-id="{}"'.format(uid)
    selector = 'article[{}] .teaser-small__kicker-logo--tag'.format(attr)
    assert text in browser.cssselect(selector)[0].getparent().text_content()


def test_d18_icon_is_not_display_on_zplus_teaser(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set(
        'tag_logos', 'reader_revenue')
    browser = testbrowser('/zeit-online/centerpage/taglogo-d18')
    assert not browser.cssselect(
        'teaser-small__kicker-logo--zplus + .teaser-small__kicker-logo--tag')
    assert not browser.cssselect(
        '.teaser-small__kicker-logo--tag + .teaser-small__kicker-logo--zplus')


def test_d18_icon_is_not_display_on_zmo_teaser(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set(
        'tag_logos', 'reader_revenue')
    browser = testbrowser('/zeit-online/centerpage/taglogo-d18')
    assert not browser.cssselect(
        'teaser-small__kicker-logo--zmo + .teaser-small__kicker-logo--tag')
    assert not browser.cssselect(
        '.teaser-small__kicker-logo--tag + .teaser-small__kicker-logo--zmo')


def test_d18_icon_is_not_display_on_d18_teaser(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set(
        'tag_logos', 'reader_revenue')
    browser = testbrowser('/zeit-online/parquet')
    assert not browser.cssselect(
        '.cp-area--d18-parquet .teaser-large__kicker-logo--tag')


def test_d18_icon_is_display_on_auto_area(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set(
        'tag_logos', 'reader_revenue')
    browser = testbrowser('/zeit-online/centerpage/taglogo-d18')
    query = ('.cp-region--solo + .cp-region--duo article:first-child')
    assert browser.cssselect(query)


def test_d18_icon_is_display_on_nextread(testbrowser):
    browser = testbrowser('/zeit-online/article/simple-nextread-taglogo')
    assert browser.cssselect('article.nextread .nextread__kicker-logo--tag')


def test_zett_icon_is_display_on_nextread(testbrowser):
    browser = testbrowser('/zeit-online/article/simple-nextread-zett')
    assert browser.cssselect('article.nextread .nextread__kicker-logo--zett')


def test_zco_icon_is_display_on_nextread(testbrowser):
    browser = testbrowser('/zeit-online/article/simple-nextread-zco')
    assert browser.cssselect('article.nextread .nextread__kicker-logo--zco')


def test_gallery_teaser_respects_hidden_slides(testbrowser):
    browser = testbrowser('/zeit-online/teaser-gallery-setup')
    article = browser.cssselect('article[data-unique-id="{}"]'.format(
        'http://xml.zeit.de/galerien/fs-desktop-schreibtisch-computer'))[0]
    counter = article.cssselect('.teaser-gallery__counter')[0]
    assert counter.text == '13 Fotos'


def test_gallery_teaser_handles_articles_with_inline_galleries(testbrowser):
    browser = testbrowser('/zeit-online/teaser-gallery-setup')
    article = browser.cssselect('article[data-unique-id="{}"]'.format(
        'http://xml.zeit.de/zeit-online/article/inline-gallery'))[0]
    counter = article.cssselect('.teaser-gallery__counter')[0]
    assert counter.text == '7 Fotos'


def test_centerpage_can_include_optimizely(testbrowser):
    browser = testbrowser('/zeit-online/slenderized-centerpage')
    assert 'optimizely' not in browser.contents

    optimizely_url = '//cdn.optimizely.com/js/281825380.js'
    settings = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    settings['optimizely_on_zon_centerpage'] = optimizely_url
    browser = testbrowser('/zeit-online/slenderized-centerpage')
    assert optimizely_url in browser.contents


def test_ressortpage_returns_is_ressortpage_correctly(
        application, dummy_request):
    cp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/index')
    view = zeit.web.site.view_centerpage.Centerpage(cp, dummy_request)
    assert not view.is_ressortpage

    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/centerpage/centerpage')
    view = zeit.web.site.view_centerpage.Centerpage(cp, dummy_request)
    assert view.is_ressortpage

    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/angebote/leseperlen')
    view = zeit.web.site.view_centerpage.Centerpage(cp, dummy_request)
    assert not view.is_ressortpage


def test_special_ressortpage_returns_is_ressortpage_correctly(
        application, monkeypatch, dummy_request):

    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/main-teaser-setup')
    monkeypatch.setattr(
        zeit.web.site.view_centerpage.Centerpage, u'ressort', u'mobilitaet')
    view = zeit.web.site.view_centerpage.Centerpage(cp, dummy_request)
    assert view.is_ressortpage


def test_hp_should_include_itunes_smart_app_banner(testbrowser):
    browser = testbrowser('/zeit-online/slenderized-index')
    app_banner_id = browser.cssselect('meta[name="apple-itunes-app"]')
    assert len(app_banner_id) == 1
    assert app_banner_id[0].get('content') == 'app-id=828889166'


def test_cp_should_not_include_itunes_smart_app_banner(testbrowser):
    browser = testbrowser('/zeit-online/centerpage/centerpage')
    app_banner_id = browser.cssselect('meta[name="apple-itunes-app"]')
    assert len(app_banner_id) == 0


def test_zar_parquet_is_rendering(testbrowser):
    browser = testbrowser('/zeit-online/parquet')

    zar_parquet = browser.cssselect('.cp-area--zar-parquet')[0]
    title = zar_parquet.cssselect('.parquet-meta__title')
    logo = zar_parquet.cssselect('.parquet-meta__logo')
    teaser = zar_parquet.cssselect('article')
    more_link = zar_parquet.cssselect('.parquet-meta__more-link')

    assert len(title)
    assert len(logo)
    assert len(more_link)
    assert len(teaser) == 3


def test_responsive_image_fullwidth_teaser_has_correct_structure(testbrowser):
    browser = testbrowser('/zeit-online/fullwidth-teaser')
    sel = browser.cssselect

    assert len(sel('.teaser-fullwidth__media')) == 5
    assert len(sel('picture.teaser-fullwidth__media-container')) == 5


def test_responsive_image_classic_teaser_has_correct_structure(testbrowser):
    browser = testbrowser('/zeit-online/classic-teaser')
    sel = browser.cssselect

    # only the first region has the responsive-image teaser
    assert len(sel('.teaser-classic__media')) == 4
    assert len(sel('picture.teaser-classic__media-container')) == 3
    assert len(sel('div.teaser-classic__media-container')) == 1


def test_responsive_image_teaser_only_in_first_region(testbrowser):
    browser = testbrowser('/zeit-online/journalistic-formats')
    sel = browser.cssselect

    assert len(sel('.teaser-fullwidth__media')) == 3
    assert len(sel('picture.teaser-fullwidth__media-container')) == 1
    assert len(sel('div.teaser-fullwidth__media-container')) == 2

    assert len(sel('.teaser-classic__media')) == 3
    assert len(sel('picture.teaser-classic__media-container')) == 1
    assert len(sel('div.teaser-classic__media-container')) == 2


def test_topicpage_has_jsonld(testbrowser, data_solr):
    browser = testbrowser('/thema/jurastudium')
    assert browser.cssselect('script[type="application/ld+json"]')
    assert '"@type": "ItemList"' in browser.contents


def test_centerpage_has_no_jsonld(testbrowser, data_solr):
    browser = testbrowser('/zeit-online/index')
    assert 'ld+json' not in browser.contents


def test_brandeins_teaser_kicker_should_contain_logo(testbrowser):
    browser = testbrowser('/zeit-online/centerpage/teasers-to-brandeins')

    teaser_fullwidth_logo = browser.cssselect(
        '.teaser-fullwidth__kicker-logo--brandeins')
    teaser_classic_logo = browser.cssselect(
        '.teaser-classic__kicker-logo--brandeins')
    teaser_large_logo = browser.cssselect(
        '.teaser-large__kicker-logo--brandeins')
    teaser_small_logo = browser.cssselect(
        '.teaser-small__kicker-logo--brandeins')
    teaser_small_minor_logo = browser.cssselect(
        '.teaser-small-minor__kicker-logo--brandeins')
    teaser_square_logo = browser.cssselect(
        '.teaser-square__kicker-logo--brandeins')

    assert len(teaser_fullwidth_logo) == 1
    assert len(teaser_classic_logo) == 1
    assert len(teaser_large_logo) == 2
    assert len(teaser_small_logo) == 4
    assert len(teaser_small_minor_logo) == 2
    assert len(teaser_square_logo) == 2


def test_brandeins_teaser_should_force_mobile_images(testbrowser):
    browser = testbrowser('/zeit-online/centerpage/teasers-to-brandeins')
    figures = browser.cssselect('.cp-area--brandeins .teaser-small__media')

    assert figures
    for figure in figures:
        assert 'teaser-small__media--force-mobile' in figure.get('class')


def test_brandeins_teaser_should_display_its_image_on_mobile(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.set_window_size(320, 480)
    driver.get('%s/zeit-online/parquet-feeds' % testserver.url)
    teaser_images = driver.find_elements_by_css_selector(
        '.cp-area--brandeins .teaser-small__media')

    assert len(teaser_images)

    for image in teaser_images:
        assert ('teaser-small__media--force-mobile' in
                image.get_attribute('class'))
        assert image.is_displayed()
