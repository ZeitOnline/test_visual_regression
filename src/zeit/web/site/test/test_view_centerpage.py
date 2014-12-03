# -*- coding: utf-8 -*-
import lxml
import mock
import pytest

import zeit.web.site.view_centerpage


screen_sizes = ((320, 480, True), (520, 960, True),
                (768, 1024, False), (980, 1024, False))


@pytest.fixture(scope='session', params=screen_sizes)
def screen_size(request):
    return request.param


def test_area_main_should_filter_teasers():
    context = mock.MagicMock()

    def create_mocked_teaserblocks():
        tb_large = mock.MagicMock()
        tb_large.layout.id = 'zon-large'
        tb_large.__len__.return_value = 2
        tb_large.__iter__.return_value = iter(['article'])

        tb_small = mock.MagicMock()
        tb_small.layout.id = 'zon-small'
        tb_small.__len__.return_value = 2
        tb_small.__iter__.return_value = iter(['article'])

        tb_no_layout = mock.MagicMock()
        tb_no_layout.layout = None
        tb_no_layout.__len__.return_value = 2

        tb_no_layout_id = mock.MagicMock()
        tb_no_layout_id.layout.id = None
        tb_no_layout_id.__len__.return_value = 2

        tb_no_teaser_in_block = mock.MagicMock()
        tb_no_teaser_in_block.layout.id = 'zon-small'
        tb_no_teaser_in_block.__iter__.return_value = iter([])

        return [tb_large, tb_small, tb_no_layout, tb_no_layout_id,
                tb_no_teaser_in_block]

    context['lead'].values = create_mocked_teaserblocks

    request = mock.Mock()
    cp = zeit.web.site.view_centerpage.Centerpage(context, request)

    assert len(cp.area_main) == 2
    assert cp.area_main[0][0] == 'zon-large'
    assert cp.area_main[0][1] == 'article'
    assert cp.area_main[1][0] == 'zon-small'
    assert cp.area_main[0][1] == 'article'


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

    teaser = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/artikel/01')
    teaser.uniqueId = 'http://xml.zeit.de/artikel/header1'
    teaser.teaserSupertitle = 'teaserSupertitle'
    teaser.teaserTitle = 'teaserTitle'
    teaser.teaserText = 'teaserText'

    html_str = tpl.render(teaser=teaser)
    html = lxml.html.fromstring(html_str).cssselect

    assert len(html('article.teaser h2.teaser__heading')) == 1, (
        'No headline is present')

    link = html('a.teaser__combined-link')[0]
    assert link.attrib['href'] == 'http://xml.zeit.de/artikel/header1', (
        'No link is present')
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
    assert len(teaser_datetime.text), 'No datetime present'

    assert teaser_datetime.attrib['datetime'] == '2013-10-08 09:25', (
        'No datetime attrib present')

    teaser_co = html('div.teaser__metadata > a.teaser__commentcount')[0]

    assert teaser_co.attrib['href'] == teaser.uniqueId + '#comments', (
        'No comment link present')

    assert teaser_co.attrib['title'] == '9 Kommentare', (
        'No comment link present')

    assert teaser_co.text == '9 Kommentare', (
        'No comment text present')


def test_first_small_teaser_has_image_on_mobile_mode(
        selenium_driver, testserver):

    driver = selenium_driver
    driver.set_window_size(320, 480)
    driver.get('%s/zeit-online/fullwidth-onimage-teaser' % testserver.url)
    box = driver.find_elements_by_class_name('teaser-collection')[0]
    first = box.find_elements_by_class_name('teaser-small__media')[0]
    second = box.find_elements_by_class_name('teaser-small__media')[1]

    assert first.is_displayed(), 'image is not displayed'
    assert second.is_displayed() is False, 'image is displayed'


def test_fullwidth_teaser_should_be_rendered(testserver, testbrowser):

    browser = testbrowser('%s/zeit-online/fullwidth-teaser' % testserver.url)

    teaser_box = browser.cssselect('.teasers-fullwidth')
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
        assert helper.size.get('width') == 626


def test_main_teasers_should_be_rendered_correctly(testserver, testbrowser):
    browser = testbrowser(
        '%s/zeit-online/main-teaser-setup' % testserver.url)

    articles = browser.cssselect('.teaser-collection--main .teasers article')
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
        '#main .teaser-collection .teasers'
        ' article:first-of-type figure.scaled-image'
        ' a > img')
    assert len(image) == 1, 'Only one image for first article'


def test_image_should_be_on_position_b(testserver, testbrowser):
    browser = testbrowser(
        '%s/zeit-online/main-teaser-setup' % testserver.url)
    articles = browser.cssselect('#main .teaser-collection .teasers article')

    assert articles[0][1].tag == 'figure', 'An img should be on this position'


def test_image_should_be_on_position_a(testserver, testbrowser):
    browser = testbrowser(
        '%s/zeit-online/main-teaser-setup' % testserver.url)
    articles = browser.cssselect('#main .teaser-collection .teasers article')

    assert articles[1][0].tag == 'figure', 'An img should be on this position'


def test_responsive_image_should_have_noscript(testserver, testbrowser):
    browser = testbrowser(
        '%s/zeit-online/main-teaser-setup' % testserver.url)

    noscript = browser.cssselect(
        '#main .teaser-collection .teasers article figure noscript')
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

    view = zeit.web.site.view_centerpage.Centerpage(mycp, mock.Mock())

    assert view.topiclinks == [('Label 1', 'http://link_1'),
                               ('Label 2', 'http://link_2'),
                               ('Label 3', 'http://link_3')]


def test_main_areas_should_be_rendered_correctly(testserver, testbrowser):
    browser = testbrowser(
        '%s/zeit-online/fullwidth-onimage-teaser' % testserver.url)

    fullwidth = browser.cssselect('.main .main__fullwidth')
    content = browser.cssselect('.main .main__content')
    informatives = browser.cssselect('.main .main__informatives')

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
    assert font == "TabletGothic", 'teaser column font is wrong'


def test_series_teaser_should_render_series_element(testserver, testbrowser):

    browser = testbrowser(
        '%s/zeit-online/teaser-serie-setup' % testserver.url)

    series_element = browser.cssselect('.teaser-series__label')
    assert len(series_element) == 1
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

    pad_script = 'return $(".teaser-series--hasmedia").css("padding-left")'
    padding = driver.execute_script(pad_script)

    border_script = 'return $(".teaser-series").css("border-top-style")'
    border = driver.execute_script(border_script)

    if screen_size[0] == 320:
        assert width > 250, 'mobile: imgage box of wrong size'
        assert padding == u'0px', 'mobile: box layout wrong'
        assert border == 'solid', 'mobile: border-top wrong'
    elif screen_size[0] == 520:
        assert width == 150, 'phablet: imgage box of wrong size'
        assert padding == u'170px', 'phablet: box layout wrong'
        assert border == 'dotted', 'phablet: border-top wrong'
    elif screen_size[0] == 768:
        assert width == 150, 'ipad: imgage box of wrong size'
        assert padding == u'170px', 'ipad: box layout wrong'
        assert border == 'dotted', 'ipad: border-top wrong'
    else:
        assert width == 250, 'desktop: image box of wrong size'
        assert padding == u'270px', 'desktop: box layout wrong'
        assert border == 'dotted', 'desktop: border-top wrong'
