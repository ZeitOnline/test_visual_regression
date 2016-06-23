# -*- coding: utf-8 -*-
import re

import mock
import pytest
import pyramid.threadlocal

import zeit.cms.interfaces

import zeit.web.core.utils
import zeit.web.core.template


@pytest.fixture
def monkeyreq(monkeypatch):
    def request():
        m = mock.Mock()
        m.route_url = lambda x: "http://example.com/"
        m.image_host = 'http://example.com'
        return m

    monkeypatch.setattr(pyramid.threadlocal, "get_current_request", request)


def test_cp_should_have_buzz_module(testbrowser):
    browser = testbrowser('/zeit-magazin/buzz')
    assert '<section class="buzzboard">' in browser.contents
    assert '<table class="buzzboard__table' in browser.contents
    assert '<div class="buzzboard__container">' in browser.contents


def test_get_reaches_from_centerpage_view(application):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/buzz')
    block = zeit.web.core.utils.find_block(
        cp, module='zmo-mostread')
    buzz = zeit.web.core.template.get_module(block).reach

    buzz_views = buzz.get_views(section='zeit-magazin')[1].score
    buzz_facebook = buzz.get_social(
        facet='facebook', section='zeit-magazin')[1].score
    buzz_comments = buzz.get_comments(section='zeit-magazin')[1].score

    assert buzz_views == 73147
    assert buzz_facebook == 408
    assert buzz_comments == 461


def test_teaser_square_large_has_correct_markup(testbrowser):
    browser = testbrowser('/zeit-magazin/teaser-square-large')
    element = browser.cssselect('.teaser-square-large')[0]

    text_wrap = element.cssselect('.teaser-square-large__text')
    link_wrap = element.cssselect('a')
    image_wrap = element.cssselect('.teaser-square-large__media')
    supertitle = element.cssselect('.teaser-square-large__kicker')[0]
    title = element.cssselect('.teaser-square-large__title')[0]
    subtitle = element.cssselect('.teaser-square-large__subtitle')[0]
    img = element.cssselect('img')[0]

    assert len(text_wrap) != 0
    assert len(link_wrap) == 2
    assert len(image_wrap) != 0
    assert supertitle.text.strip() == u'Raffiniert kochen'
    assert title.text.strip() == 'Die perfekte Illusion'
    assert u'Safran, Salzzitronen' in subtitle.text.strip()
    assert re.search('frau-isst-suppe-2/square',
                     img.get('src'))
    assert img.get('alt') == 'Eine Frau isst Paprikasuppe'


def test_teaser_square_large_light_has_correct_markup(testbrowser):
    browser = testbrowser('/zeit-magazin/teaser-square-large')
    element = browser.cssselect('.teaser-square-large--light')[0]

    text_wrap = element.cssselect('.teaser-square-large__text')
    link_wrap = element.cssselect('a')
    image_wrap = element.cssselect('.teaser-square-large__media')
    supertitle = element.cssselect('.teaser-square-large__kicker')[0]
    title = element.cssselect('.teaser-square-large__title')[0]
    subtitle = element.cssselect('.teaser-square-large__subtitle')[0]
    img = element.cssselect('img')[0]

    assert len(text_wrap) != 0
    assert len(link_wrap) == 2
    assert len(image_wrap) != 0
    assert supertitle.text.strip() == u'Raffiniert kochen'
    assert title.text.strip() == 'Die perfekte Illusion'
    assert u'Safran, Salzzitronen' in subtitle.text.strip()
    assert re.search('frau-isst-suppe-2/square',
                     img.get('src'))
    assert img.get('alt') == 'Eine Frau isst Paprikasuppe'


def test_teaser_landscape_small_has_correct_markup(testbrowser):
    browser = testbrowser('/zeit-magazin/teaser-landscape-small')
    element = browser.cssselect('.teaser-landscape-small')

    text_wrap = element[0].cssselect('.teaser-landscape-small__text')
    link_wrap = element[0].cssselect('a')
    image_wrap = element[0].cssselect('.teaser-landscape-small__media')
    supertitle = element[0].cssselect('.teaser-landscape-small__kicker')[0]
    title = element[0].cssselect('.teaser-landscape-small__title')[0]
    subtitle = element[0].cssselect('.teaser-landscape-small__subtitle')[0]
    img = element[0].cssselect('img')[0]

    assert len(text_wrap) != 0
    assert len(link_wrap) == 2
    assert len(image_wrap) != 0
    assert supertitle.text.strip() == u'Raffiniert kochen'
    assert title.text.strip() == 'Die perfekte Illusion'
    assert u'Safran, Salzzitronen' in subtitle.text.strip()
    assert re.search('frau-isst-suppe-2/wide__822x462',
                     img.get('src'))
    assert img.get('alt') == 'Eine Frau isst Paprikasuppe'


def test_teaser_upright_has_correct_markup(testbrowser):
    browser = testbrowser('/zeit-magazin/teaser-upright')
    element = browser.cssselect('.teaser-upright')

    text_wrap = element[0].cssselect('.teaser-upright__text')
    link_wrap = element[0].cssselect('a')
    icon = element[0].cssselect('.teaser-upright__gallery-icon')
    img = element[0].cssselect('img')[0]
    assert len(text_wrap) != 0
    assert len(link_wrap) == 2
    assert len(icon) == 1
    assert '/exampleimages/artikel/01/schoppenstube/tile__' in img.get('src')


def test_teaser_upright_large_has_correct_markup(testbrowser):
    browser = testbrowser('zeit-magazin/teaser-upright-large')
    element = browser.cssselect('.teaser-upright-large')

    text_wrap = element[0].cssselect('.teaser-upright-large__text')
    link_wrap = element[0].cssselect('a')
    image_wrap = element[0].cssselect('.teaser-upright-large__media')
    supertitle = element[0].cssselect('.teaser-upright-large__kicker')[0]
    title = element[0].cssselect('.teaser-upright-large__title')[0]
    subtitle = element[0].cssselect('.teaser-upright-large__subtitle')[0]
    img = element[0].cssselect('img')[0]

    assert len(text_wrap) != 0
    assert len(link_wrap) == 2
    assert len(image_wrap) != 0
    assert supertitle.text.strip() == u'Raffiniert kochen'
    assert title.text.strip() == 'Die perfekte Illusion'
    assert u'Safran, Salzzitronen' in subtitle.text.strip()
    assert re.search('frau-isst-suppe-2/tile__660x660',
                     img.get('src'))
    assert img.get('alt') == 'Eine Frau isst Paprikasuppe'


def test_teaser_landscape_large_has_correct_markup(testbrowser):
    browser = testbrowser('/zeit-magazin/teaser-landscape-large')
    element = browser.cssselect('.teaser-landscape-large')

    text_wrap = element[0].cssselect('.teaser-landscape-large__text')
    link_wrap = element[0].cssselect('a')
    supertitle = element[0].cssselect(
        '.teaser-landscape-large__kicker')[0]
    title = element[0].cssselect('.teaser-landscape-large__title')[0]
    subtitle = element[0].cssselect('.teaser-landscape-large__subtitle')[0]
    img = element[0].cssselect('img')[0]

    assert len(text_wrap) != 0
    assert len(link_wrap) == 2
    assert supertitle.text.strip() == u'Raffiniert kochen'
    assert title.text.strip() == 'Die perfekte Illusion'
    assert u'Safran, Salzzitronen' in subtitle.text.strip()
    assert re.search('frau-isst-suppe-2/wide__822x462',
                     img.get('src'))
    assert img.get('alt') == 'Eine Frau isst Paprikasuppe'


def test_teaser_landscape_large_photo_has_correct_markup(testbrowser):
    browser = testbrowser('/zeit-magazin/teaser-landscape-large-photo')
    element = browser.cssselect('.teaser-landscape-large-photo')

    text_wrap = element[0].cssselect('.teaser-landscape-large-photo__text')
    link_wrap = element[0].cssselect('a')
    supertitle = element[0].cssselect(
        '.teaser-landscape-large-photo__kicker')[0]
    title = element[0].cssselect('.teaser-landscape-large-photo__title')[0]

    assert len(text_wrap) != 0
    assert len(link_wrap) == 2
    assert supertitle.text.strip() == u'Raffiniert kochen'
    assert title.text.strip() == u'Die perfekte Illusion'


def test_teaser_fullwidth_with_video_has_correct_markup(
        testbrowser, testserver):
    browser = testbrowser('/zeit-magazin/teaser-fullwidth')
    teaser = browser.cssselect('.teaser-fullwidth')[2]

    vid_wrap = teaser.cssselect('.teaser-fullwidth__media-container')[0]
    img = teaser.cssselect('img')[0]
    title_wrap = teaser.cssselect('a')[1]
    a = teaser.cssselect('a')
    title = teaser.cssselect('.teaser-fullwidth__title')
    subtitle = teaser.cssselect('.teaser-fullwidth__subtitle')
    source1 = teaser.cssselect('source')[0].get('src')
    source2 = teaser.cssselect('source')[1].get('src')

    src1_val = \
        'http://brightcove.vo.llnwd.net/pd15/media/18140073001/'\
        '201401/1105/18140073001_3035966678001_Beitrag'\
        '-Skispringen-f-r-Anf-nger.mp4'
    src2_val = \
        'http://live0.zeit.de/multimedia/videos/3035864892001.webm'
    src_img = \
        'http://live0.zeit.de/multimedia/'\
        'videos/3035864892001.jpg'

    # structure
    assert img.get('class') == 'video--fallback '
    assert 'teaser-fullwidth__text' in title_wrap.get('class')
    assert len(title) == 1
    assert len(subtitle) == 1

    # content
    assert vid_wrap.get('data-backgroundvideo') == '3035864892001'
    assert 'Es leben' in subtitle[0].text.strip()
    assert img.get('src') == src_img
    assert title[0].text.strip() == 'und der Titel dazu'
    assert source1 == src1_val
    assert source2 == src2_val

    # links
    assert len(a) == 2


def test_teaser_fullwidth_light_with_video_has_correct_markup(
        testbrowser, testserver):
    browser = testbrowser('/zeit-magazin/teaser-fullwidth')
    teaser = browser.cssselect('.teaser-fullwidth--light')[1]

    vid_wrap = teaser.cssselect('.teaser-fullwidth__media-container')[0]
    img = teaser.cssselect('img')[0]
    title_wrap = teaser.cssselect('a')[1]
    a = teaser.cssselect('a')
    title = teaser.cssselect('.teaser-fullwidth__title')
    subtitle = teaser.cssselect('.teaser-fullwidth__subtitle')
    source1 = teaser.cssselect('source')[0].get('src')
    source2 = teaser.cssselect('source')[1].get('src')

    src1_val = \
        'http://brightcove.vo.llnwd.net/pd15/media/18140073001/'\
        '201401/1105/18140073001_3035966678001_Beitrag'\
        '-Skispringen-f-r-Anf-nger.mp4'
    src2_val = \
        'http://live0.zeit.de/multimedia/videos/3035864892001.webm'
    src_img = \
        'http://live0.zeit.de/multimedia/'\
        'videos/3035864892001.jpg'

    # structure
    assert img.get('class') == 'video--fallback '
    assert 'teaser-fullwidth__text' in title_wrap.get('class')
    assert len(title) == 1
    assert len(subtitle) == 1

    # content
    assert vid_wrap.get('data-backgroundvideo') == '3035864892001'
    assert 'Es leben' in subtitle[0].text.strip()
    assert img.get('src') == src_img
    assert title[0].text.strip() == 'und der Titel dazu'
    assert source1 == src1_val
    assert source2 == src2_val

    # links
    assert len(a) == 2


def test_teaser_fullwidth_with_image_has_correct_markup(
        testbrowser, testserver):
    browser = testbrowser('/zeit-magazin/teaser-fullwidth')
    teaser = browser.cssselect('.teaser-fullwidth')[0]

    img_wrap = teaser.cssselect('.teaser-fullwidth__media-container')
    img = teaser.cssselect('img')[0]
    title_wrap = teaser.cssselect('a')[1]
    a = teaser.cssselect('a')
    title = teaser.cssselect('.teaser-fullwidth__title')
    subtitle = teaser.cssselect('.teaser-fullwidth__subtitle')
    image_pattern = '/lamm-aubergine/wide__'

    # structure
    assert len(img_wrap) != 0
    assert len(title_wrap) != 0

    assert image_pattern in img.get('src')
    assert u'Probier' in title[0].text.strip()
    assert u'auch dieses Jahr leider' in subtitle[0].text.strip()
    assert 'Lammkotelett' in img.get('alt')

    # links
    assert len(a) == 2


def test_teaser_fullwidth_light_with_image_has_correct_markup(
        testbrowser, testserver):
    browser = testbrowser('/zeit-magazin/teaser-fullwidth')
    teaser = browser.cssselect('.teaser-fullwidth--light')[0]

    img_wrap = teaser.cssselect('.teaser-fullwidth__media-container')
    img = teaser.cssselect('img')[0]
    title_wrap = teaser.cssselect('a')[1]
    a = teaser.cssselect('a')
    title = teaser.cssselect('.teaser-fullwidth__title')
    subtitle = teaser.cssselect('.teaser-fullwidth__subtitle')
    image_pattern = '/lamm-aubergine/wide__'

    # structure
    assert len(img_wrap) != 0
    assert len(title_wrap) != 0

    assert image_pattern in img.get('src')
    assert u'Probier' in title[0].text.strip()
    assert u'auch dieses Jahr leider' in subtitle[0].text.strip()
    assert 'Lammkotelett' in img.get('alt')

    # links
    assert len(a) == 2


def test_teaser_print_cover_has_correct_markup(testbrowser):
    browser = testbrowser('/zeit-magazin/teaser-print-cover')
    element = browser.cssselect('.teaser-print-cover')[0]

    text_wrap = element.cssselect('.teaser-print-cover__text')
    link_wrap = element.cssselect('a')
    image_wrap = element.cssselect('.teaser-print-cover__media')
    supertitle = element.cssselect('.teaser-print-cover__kicker')[0]
    title = element.cssselect('.teaser-print-cover__title')[0]
    img = element.cssselect('img')[0]

    assert len(text_wrap) != 0
    assert len(link_wrap) == 2
    assert len(image_wrap) != 0
    assert supertitle.text.strip() == 'ZEITmagazin'
    assert 'Das neue Heft' in title.text.strip()
    assert 'exampleimages/artikel/02/heft/original' in img.get('src')


def test_teaser_mtb_square_has_correct_markup(testbrowser):
    browser = testbrowser('/zeit-magazin/teaser-mtb-square')
    element = browser.cssselect('.teaser-mtb-square')[0]

    text_wrap = element.cssselect('.teaser-mtb-square__text')
    link_wrap = element.cssselect('a')
    image_wrap = element.cssselect('.teaser-mtb-square__media')
    supertitle = element.cssselect('.teaser-mtb-square__kicker')[0]
    title = element.cssselect('.teaser-mtb-square__title')[0]
    img = element.cssselect('img')[0]

    assert len(text_wrap) != 0
    assert len(link_wrap) == 2
    assert len(image_wrap) != 0
    assert supertitle.text.strip() == 'Serie Gesellschaftskritik'
    assert 'schlechte Laune' in title.text.strip()
    assert 'grumpy-cat/square' in img.get('src')


def test_trio_area_has_title(testbrowser):
    browser = testbrowser('/zeit-magazin/teaser-mtb-square')
    title = browser.cssselect('.cp-area__title')[0]
    assert 'Dinge Wohnen' in title.text


def test_teaser_should_have_comment_count(testbrowser, mockserver_factory):

    cp_counts = """<?xml version="1.0" encoding="UTF-8"?>
    <nodes>
         <node comment_count="129"
               url="/zeit-magazin/article/essen-geniessen-spargel-lamm"/>
    </nodes>
    """
    mockserver_factory(cp_counts)
    browser = testbrowser('/zeit-magazin/index')
    counts = browser.cssselect('.cp_comment__count')
    assert int(counts[0].text) == 129


def test_default_teaser_should_return_default_teaser_image(
        application, testserver, testbrowser):
    cp = 'http://xml.zeit.de/zeit-magazin/teaser-upright'
    cp_context = zeit.cms.interfaces.ICMSContent(cp)

    teaser_block = cp_context[0][0][0]
    article = 'http://xml.zeit.de/zeit-magazin/article/artikel-ohne-assets'
    article_context = zeit.cms.interfaces.ICMSContent(article)
    teaser_img = zeit.web.core.template.get_image(
        teaser_block, article_context)
    assert zeit.web.core.interfaces.ITeaserImage.providedBy(teaser_img)


def test_zmo_homepage_identifies_itself_as_homepage(testserver):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/index')
    view = zeit.web.magazin.view_centerpage.Centerpage(cp, mock.Mock())
    assert view.is_hp is True
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/misc')
    view = zeit.web.magazin.view_centerpage.Centerpage(cp, mock.Mock())
    assert view.is_hp is False


def test_card_teaser_keeps_transparent_image_background(testbrowser):
    browser = testbrowser('/zeit-magazin/teaser-card')
    teaser_img = browser.cssselect(
        '.teaser-card[data-unique-id$=martenstein-portraitformat] img')[0]
    assert 'ccddee' not in teaser_img.attrib['data-src']


def test_card_background_setting_on_teaser_overrides_article_setting(
        testbrowser):
    browser = testbrowser('/zeit-magazin/teaser-card')
    card = browser.cssselect(
        '.teaser-card[data-unique-id$=martenstein-portraitformat] .card')[0]
    assert 'a1f88c' in card.attrib['style']


def test_centerpage_should_have_default_keywords(testbrowser):
    # Default means ressort and sub ressort respectively
    browser = testbrowser('/zeit-magazin/centerpage/lebensart-2')
    keywords = browser.cssselect('meta[name="keywords"]')[0]
    assert keywords.get('content') == 'Lebensart, Mode-Design'


def test_centerpage_should_have_page_meta_keywords(testbrowser):
    browser = testbrowser('/zeit-magazin/centerpage/lebensart')
    assert '<meta name="keywords" content="Pinguin">' in (
        browser.contents)


def test_centerpage_should_have_page_meta_robots_information(testbrowser):
    # SEO robots information is given
    browser = testbrowser('/zeit-magazin/centerpage/lebensart')
    meta_robots = browser.document.xpath('//meta[@name="robots"]/@content')
    assert 'my, personal, seo, robots, information' in meta_robots
    # No SEO robots information is given
    browser = testbrowser('/zeit-magazin/index')
    meta_robots = browser.document.xpath('//meta[@name="robots"]/@content')
    assert 'index,follow,noodp,noydir,noarchive' in meta_robots


def test_get_teaser_template_should_produce_correct_combinations():
    templates_path = 'zeit.web.magazin:templates/inc/teaser/'
    should = [
        templates_path + 'teaser_lead_article_video.html',
        templates_path + 'teaser_lead_article_default.html',
        templates_path + 'teaser_lead_default_video.html',
        templates_path + 'teaser_lead_default_default.html',
        templates_path + 'teaser_default_article_video.html',
        templates_path + 'teaser_default_article_default.html',
        templates_path + 'teaser_default_default_video.html',
        templates_path + 'teaser_default_default_default.html']
    result = get_teaser_template('lead', 'article', 'video')
    assert result == should
    should = [
        templates_path + 'teaser_lead_article_video.html',
        templates_path + 'teaser_lead_article_gallery.html',
        templates_path + 'teaser_lead_article_imagegroup.html',
        templates_path + 'teaser_lead_article_default.html',
        templates_path + 'teaser_lead_default_video.html',
        templates_path + 'teaser_lead_default_gallery.html',
        templates_path + 'teaser_lead_default_imagegroup.html',
        templates_path + 'teaser_lead_default_default.html',
        templates_path + 'teaser_default_article_video.html',
        templates_path + 'teaser_default_article_gallery.html',
        templates_path + 'teaser_default_article_imagegroup.html',
        templates_path + 'teaser_default_article_default.html',
        templates_path + 'teaser_default_default_video.html',
        templates_path + 'teaser_default_default_gallery.html',
        templates_path + 'teaser_default_default_imagegroup.html',
        templates_path + 'teaser_default_default_default.html']
    assets = ('video', 'gallery', 'imagegroup')
    result = get_teaser_template('lead', 'article', assets)
    assert result == should


def test_autoselected_asset_from_cp_teaser_should_be_a_gallery(application):
    article = ('http://xml.zeit.de/zeit-magazin/'
               'centerpage/article_gallery_asset')
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.web.core.centerpage.auto_select_asset(context)
    assert isinstance(asset, zeit.content.gallery.gallery.Gallery)


def test_autoselected_asset_from_cp_teaser_should_be_an_image(application):
    article = ('http://xml.zeit.de/zeit-magazin/'
               'centerpage/article_image_asset')
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.web.core.centerpage.auto_select_asset(context)
    assert isinstance(asset, zeit.content.image.imagegroup.ImageGroup)


def test_autoselected_asset_from_cp_teaser_should_be_a_video(application):
    article = 'http://xml.zeit.de/zeit-magazin/article/article_video_asset'
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.web.core.centerpage.auto_select_asset(context)
    assert isinstance(asset, zeit.content.video.video.Video)


def test_autoselected_asset_from_cp_teaser_should_be_a_video_list(application):
    url = 'http://xml.zeit.de/zeit-magazin/article/article_video_asset_list'
    context = zeit.cms.interfaces.ICMSContent(url)
    asset = zeit.web.core.centerpage.auto_select_asset(context)
    assert isinstance(asset[0], zeit.content.video.video.Video)
    assert isinstance(asset[1], zeit.content.video.video.Video)


def test_get_image_asset_should_return_image_asset(application):
    article = ('http://xml.zeit.de/zeit-magazin/'
               'centerpage/article_image_asset')
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.web.core.centerpage.get_image_asset(context)
    assert isinstance(asset, zeit.content.image.imagegroup.ImageGroup)


def test_get_gallery_asset_should_return_gallery_asset(application):
    article = ('http://xml.zeit.de/zeit-magazin/'
               'centerpage/article_gallery_asset')
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.web.core.centerpage.get_gallery_asset(context)
    assert isinstance(asset, zeit.content.gallery.gallery.Gallery)


def test_get_video_asset_should_return_video_asset(application):
    article = 'http://xml.zeit.de/zeit-magazin/article/article_video_asset'
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.web.core.centerpage.get_video_asset(
        context)
    assert isinstance(asset, zeit.content.video.video.Video)


def test_default_image_url_should_return_default_image_size(
        application, monkeyreq):
    image_id = ('http://xml.zeit.de/zeit-magazin/'
                'centerpage/katzencontent/katzencontent-180x101.jpg')
    image = zeit.cms.interfaces.ICMSContent(image_id)
    image_url = default_image_url(image)
    assert re.search(
        'http://example.com/zeit-magazin/centerpage/katzencontent/'
        'bitblt-.*-.*/katzencontent-180x101.jpg',
        image_url)


def test_default_image_url_should_return_available_image_size(
        application, monkeyreq):
    image_id = ('http://xml.zeit.de/zeit-magazin/'
                'centerpage/katzencontent/katzencontent-180x101.jpg')
    image = zeit.cms.interfaces.ICMSContent(image_id)
    image_url = default_image_url(image)
    assert re.search(
        'http://example.com/zeit-magazin/'
        'centerpage/katzencontent/'
        'bitblt-.*-.*/katzencontent-180x101.jpg',
        image_url)


def test_default_image_url_should_return_none_when_no_unique_id_is_given(
        application, monkeyreq):
    assert default_image_url(mock.Mock()) is None


def test_teaser_image_should_be_created_from_image_group_and_image(
        application):
    import zeit.cms.interfaces
    img = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/zeit-magazin/'
                                          'centerpage/'
                                          'katzencontent/katzencontent'
                                          '-148x84.jpg')
    imgrp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/zeit-magazin/'
                                            'centerpage/'
                                            'katzencontent/')
    teaser_image = getMultiAdapter(
        (imgrp, img),
        zeit.web.core.interfaces.ITeaserImage)

    assert teaser_image.caption == 'Die ist der image sub text '
    assert teaser_image.src == img.uniqueId
    assert teaser_image.alt == 'Die ist der Alttest'
    assert teaser_image.title == 'Katze!'


def test_wrapped_features_are_triggered(testbrowser):
    browser = testbrowser('/zeit-magazin/index')
    assert browser.cssselect('header.header')

    browser = testbrowser('/zeit-magazin/index?app-content')
    assert not browser.cssselect('header.header')
    assert browser.cssselect('body[data-is-wrapped="true"]')
