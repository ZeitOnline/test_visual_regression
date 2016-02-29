# -*- coding: utf-8 -*-
import re

from zope.component import getMultiAdapter
import mock
import pyramid.threadlocal
import pytest

from zeit.cms.checkout.helper import checked_out
import zeit.cms.interfaces
import zeit.content.gallery.gallery

from zeit.web.core.template import default_image_url
from zeit.web.core.template import get_teaser_image
from zeit.web.core.template import get_teaser_template
import zeit.web.core.centerpage
import zeit.web.magazin.view_centerpage


@pytest.fixture
def monkeyreq(monkeypatch):
    def request():
        m = mock.Mock()
        m.route_url = lambda x: "http://example.com/"
        m.image_host = 'http://example.com'
        return m

    monkeypatch.setattr(pyramid.threadlocal, "get_current_request", request)


def test_homepage_should_have_buzz_module_centerpage_should_not(testbrowser):
    browser = testbrowser('/zeit-magazin/index')
    assert '<div class="cp_buzz">' in browser.contents
    browser = testbrowser('/centerpage/lebensart')
    assert '<div class="cp_buzz">' not in browser.contents


def test_centerpage_should_have_default_keywords(testbrowser):
    # Default means ressort and sub ressort respectively
    browser = testbrowser('/centerpage/lebensart-2')
    assert '<meta name="keywords" content="Lebensart, mode-design">' in (
        browser.contents)


def test_centerpage_should_have_page_meta_keywords(testbrowser):
    browser = testbrowser('/centerpage/lebensart')
    assert '<meta name="keywords" content="Pinguin">' in (
        browser.contents)


def test_centerpage_should_have_page_meta_robots_information(testbrowser):
    # SEO robots information is given
    browser = testbrowser('/centerpage/lebensart')
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
    article = 'http://xml.zeit.de/centerpage/article_gallery_asset'
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.web.core.centerpage.auto_select_asset(context)
    assert isinstance(asset, zeit.content.gallery.gallery.Gallery)


def test_autoselected_asset_from_cp_teaser_should_be_an_image(application):
    article = 'http://xml.zeit.de/centerpage/article_image_asset'
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.web.core.centerpage.auto_select_asset(context)
    assert isinstance(asset, zeit.content.image.imagegroup.ImageGroup)


def test_autoselected_asset_from_cp_teaser_should_be_a_video(application):
    article = 'http://xml.zeit.de/centerpage/article_video_asset'
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.web.core.centerpage.auto_select_asset(context)
    assert isinstance(asset, zeit.content.video.video.Video)


def test_autoselected_asset_from_cp_teaser_should_be_a_video_list(application):
    article = 'http://xml.zeit.de/centerpage/article_video_asset_2'
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.web.core.centerpage.auto_select_asset(context)
    assert isinstance(asset[0], zeit.content.video.video.Video)
    assert isinstance(asset[1], zeit.content.video.video.Video)


def test_cp_has_lead_area(testbrowser):
    browser = testbrowser('/centerpage/lebensart')
    assert '<div class="cp_lead__wrap">' in browser.contents


def test_cp_has_informatives_area(testbrowser):
    browser = testbrowser('/centerpage/lebensart')
    assert '<div class="cp_informatives__wrap">' in browser.contents


def test_cp_lead_areas_are_available(application):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/centerpage/lebensart')
    view = zeit.web.magazin.view_centerpage.CenterpageLegacy(cp, mock.Mock())
    assert len(view.area_lead)


def test_cp_leadteaser_has_expected_structure(testbrowser):
    browser = testbrowser('/centerpage/lebensart')
    wrap = browser.cssselect('.cp_leader')
    assert len(wrap) != 0
    for element in wrap:
        text_wrap = element.cssselect('.cp_leader__title__wrap--dark')
        link_wrap = element.cssselect('a')
        image_wrap = element.cssselect('.cp_leader__asset--dark')
        assert len(text_wrap) != 0
        assert len(link_wrap) == 2
        assert len(image_wrap) != 0


def test_cp_leadteaser_has_expected_text_content(testbrowser):
    browser = testbrowser('/centerpage/lebensart')
    wrap = browser.cssselect('.cp_leader__title__wrap--dark')
    assert len(wrap) != 0
    for element in wrap:
        supertitle = element.cssselect('.cp_leader__supertitle')[0]
        title = element.cssselect('.cp_leader__title')[0]
        subtitle = element.cssselect('.cp_leader__subtitle')[0]
        assert supertitle.text.strip() == 'Article Image Asset Spitzmarke'
        assert title.text.strip() == 'Article Image Asset Titel'
        assert subtitle.text.strip() == u'Dies k\u00F6nnte'\
            ' z.B. lorem ipsum sein.'\
            ' Oder was anderes nicht ganz so langweiliges,'\
            ' zum Katzenbild passen.'


def test_cp_leadteaser_has_expected_img_content(testbrowser):
    browser = testbrowser('/centerpage/lebensart')
    wrap = browser.cssselect('.cp_leader__asset--dark')
    assert len(wrap) != 0
    for element in wrap:
        img = element.cssselect('img')[0]
        assert re.search('http://.*/centerpage/katzencontent/' +
                         'bitblt-.*/' +
                         'katzencontent-zmo-square-large.jpg',
                         img.get('src'))
        assert img.get('alt') == 'Die ist der Alttest'
        assert img.get('title') == 'Katze!'


def test_cp_leadteaser_has_expected_links(testbrowser):
    browser = testbrowser('/centerpage/lebensart')
    wrap = browser.cssselect('.cp_leader')
    assert len(wrap) != 0
    for element in wrap:
        link_wrap = element.cssselect('a')
        assert len(link_wrap) == 2
        for link in link_wrap:
            assert link.get('href') == (
                'http://localhost/centerpage/article_image_asset')


def test_cp_img_button_has_expected_structure(testbrowser):
    browser = testbrowser('/centerpage/lebensart')
    wrap = browser.cssselect('.cp_button')
    assert len(wrap) != 0
    for element in wrap:
        text_wrap = element.cssselect('.cp_button__title__wrap')
        link_wrap = element.cssselect('a')
        assert len(text_wrap) != 0
        assert len(link_wrap) >= 1


def test_cp_img_button_has_expected_img_content(testbrowser):
    browser = testbrowser('/centerpage/lebensart')
    wrap = browser.cssselect('.cp_lead__wrap .cp_button__image')
    assert len(wrap) != 0
    for element in wrap:
        img = element.cssselect('img')[0]

        image_pattern = \
            'http://.*/centerpage/katzencontent/'\
            'bitblt-.*'\
            '/katzencontent-zmo-landscape-small.jpg'
        assert re.search(image_pattern, img.get('src'))
        assert img.get('alt') == 'Die ist der Alttest'
        assert img.get('title') == 'Katze!'


def test_cp_button_has_expected_structure(testbrowser):
    browser = testbrowser('/zeit-magazin/test-cp/test-cp-zmo')
    wrap = browser.cssselect('.cp_button--small')
    assert len(wrap) != 0
    for element in wrap:
        assert len(element.cssselect('a'))
        assert len(element.cssselect('a > div img[class=" figure__media"]'))
        assert len(element.cssselect('.cp_button__title__wrap'))
        assert len(element.cssselect('header > a > h2'))
        assert len(element.cssselect(
                   'header > a > span[class="cp_button__subtitle"]'))


def test_cp_button_has_expected_text_content(testbrowser):
    browser = testbrowser('/centerpage/lebensart')
    wrap = browser.cssselect('.cp_button--small')
    assert len(wrap) != 0
    for element in wrap:
        supertitle = element.cssselect('.cp_button__supertitle')[0]
        title = element.cssselect('.cp_button__title')[0]
        subtitle = element.cssselect('.cp_button__subtitle')[0]
        assert supertitle.text.strip() == 'Article Image Asset Spitzmarke'
        assert title.text.strip() == 'Article Image Asset Titel'
        assert subtitle.text.strip() == u'Dies k\u00F6nnte'\
            ' z.B. lorem ipsum sein.'\
            ' Oder was anderes nicht ganz so langweiliges,'\
            ' zum Katzenbild passen.'


def test_cp_button_has_expected_links(testbrowser):
    browser = testbrowser('/centerpage/lebensart')
    wrap = browser.cssselect('.cp_button--small')
    assert len(wrap) != 0
    for element in wrap:
        link_wrap = element.cssselect('a')
        assert len(link_wrap) != 0
        for link in link_wrap:
            assert link.get('href') == (
                'http://localhost/centerpage/article_image_asset')


def test_cp_large_photo_button_has_expected_structure(testbrowser):
    browser = testbrowser('/zeit-magazin/test-cp/test-cp-zmo-2')
    wrap = browser.cssselect('.cp_button--large-photo')
    assert len(wrap) != 0
    for element in wrap:
        text_wrap = element.cssselect('.cp_button__title__wrap')
        link_wrap = element.cssselect('a')
        assert len(text_wrap) != 0
        assert len(link_wrap) == 2

        supertitle = element.cssselect('.cp_button__supertitle')[0]
        title = element.cssselect('.cp_button__title')[0]
        assert supertitle.text.strip() == u'Serie Gesellschaftskritik'
        assert title.text.strip() == u'Über schlechte Laune'

        for link in link_wrap:
            assert re.search(
                'http://.*/zeit-magazin/test-cp/' +
                'gesellschaftskritik-grumpy-cat',
                link.get('href'))


def test_cp_gallery_teaser_has_expected_structure(testbrowser):
    browser = testbrowser('/centerpage/lebensart')
    wrap = browser.cssselect('.cp_button--gallery')
    assert len(wrap) != 0
    for element in wrap:
        text_wrap = element.cssselect('.cp_button__title__wrap')
        link_wrap = element.cssselect('a')
        image_wrap = element.cssselect('.scaled-image')
        assert len(text_wrap) != 0
        assert len(link_wrap) == 2
        assert len(image_wrap) != 0

        supertitle = element.cssselect('.cp_button__supertitle')[0]
        title = element.cssselect('.cp_button__title')[0]
        assert supertitle.text.strip() == u'Article Image Asset Spitzmarke'
        assert title.text.strip() == u'Article Image Asset Titel'

        img = element.cssselect('img')[0]
        assert re.search('http://.*/centerpage/katzencontent/' +
                         'bitblt-.*/' +
                         'katzencontent-zmo-upright.jpg',
                         img.get('src'))
        assert img.get('alt') == 'Die ist der Alttest'
        assert img.get('title') == 'Katze!'


def test_cp_should_have_informatives_ad_at_3rd_place(testbrowser):
    browser = testbrowser('/zeit-magazin/test-cp/test-cp-zmo')
    elements = browser.cssselect('.cp_informatives__wrap > div')
    assert elements[2].get('class') == 'cp_button--ad'
    assert len(elements[2].cssselect('#ad-desktop-7')) == 1


def test_cp_with_video_lead_has_correct_markup(testbrowser):
    browser = testbrowser('/centerpage/cp_with_video_lead')
    wrap = browser.cssselect('.cp_leader--full')
    assert len(wrap) != 0
    for teaser in wrap:
        vid_wrap = teaser.cssselect('.cp_leader__asset--dark')[0]
        img = teaser.cssselect('img')[0]
        title_wrap = teaser.cssselect('header')[0]
        a = teaser.cssselect('a')
        title = teaser.cssselect('.cp_leader__title')
        subtitle = teaser.cssselect('.cp_leader__subtitle')
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
        assert title_wrap.get('class') == 'cp_leader__title__wrap'\
            ' cp_leader__title__wrap--dark'
        assert len(title) == 1
        assert len(subtitle) == 1

        # content
        assert vid_wrap.get('data-backgroundvideo') == '3035864892001'
        assert subtitle[0].text.strip() == (
            'Es leben die Skispringenden Sportredakteure!')
        assert img.get('src') == src_img
        assert title[0].text.strip() == 'und der Titel dazu'
        assert source1 == src1_val
        assert source2 == src2_val

        # links
        assert len(a) == 2
        for link in a:
            assert link.get('href') == (
                'http://localhost/centerpage/article_video_asset')


def test_cp_with_video_lead_light_has_correct_markup(testbrowser):
    browser = testbrowser('/centerpage/cp_with_video_lead-2')
    wrap = browser.cssselect('.cp_leader--full')
    assert len(wrap) != 0
    for teaser in wrap:
        vid_wrap = teaser.cssselect('.cp_leader__asset--light')[0]
        img = teaser.cssselect('img')[0]
        title_wrap = teaser.cssselect('header')[0]
        a = teaser.cssselect('a')
        title = teaser.cssselect('.cp_leader__title')
        subtitle = teaser.cssselect('.cp_leader__subtitle')
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
        assert title_wrap.get('class') == 'cp_leader__title__wrap'\
            ' cp_leader__title__wrap--light'
        assert len(title) == 1
        assert len(subtitle) == 1

        # content
        assert vid_wrap.get('data-backgroundvideo') == '3035864892001'
        assert subtitle[0].text.strip() == \
            'Es leben die Skispringenden Sportredakteure!'
        assert img.get('src') == src_img
        assert title[0].text.strip() == 'und der Titel dazu'
        assert source1 == src1_val
        assert source2 == src2_val

        # links
        assert len(a) == 2
        for link in a:
            assert link.get('href') == (
                'http://localhost/centerpage/article_video_asset')


def test_cp_with_image_lead_has_correct_markup(testbrowser):
    browser = testbrowser('/centerpage/cp_with_image_lead')
    wrap = browser.cssselect('.cp_leader--full')
    assert len(wrap) != 0
    for teaser in wrap:
        img_wrap = teaser.cssselect('.cp_leader__asset--dark')
        img = teaser.cssselect('img')[0]
        title_wrap = teaser.cssselect('header')
        a = teaser.cssselect('a')
        title = teaser.cssselect('.cp_leader__title')
        subtitle = teaser.cssselect('.cp_leader__subtitle')
        image_pattern = \
            'http://.*/centerpage/katzencontent/'\
            'bitblt-.*'\
            '/katzencontent-zmo-landscape-large.jpg'

        # structure
        assert len(img_wrap) != 0
        assert len(title_wrap) != 0

        assert re.search(image_pattern, img.get('src'))
        assert title[0].text.strip() == u'Article Image Asset Titel'
        assert subtitle[0].text.strip() == u'Dies k\u00F6nnte'\
            ' z.B. lorem ipsum sein.'\
            ' Oder was anderes nicht ganz so langweiliges,'\
            ' zum Katzenbild passen.'
        assert img.get('alt') == 'Die ist der Alttest'
        assert img.get('title') == 'Katze!'

        # links
        assert len(a) == 2
        for link in a:
            assert link.get('href') == (
                'http://localhost/centerpage/article_image_asset')


def test_lead_full_light_version_is_working(testbrowser):
    browser = testbrowser('/zeit-magazin/test-cp/test-cp-zmo-2')
    assert '<div class="cp_leader cp_leader--full">' in browser.contents
    assert '<div class="scaled-image is-pixelperfect cp_leader__asset'\
        ' cp_leader__asset--light">' in browser.contents


def test_get_image_asset_should_return_image_asset(application):
    article = 'http://xml.zeit.de/centerpage/article_image_asset'
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.web.core.centerpage.get_image_asset(context)
    assert isinstance(asset, zeit.content.image.imagegroup.ImageGroup)


def test_get_gallery_asset_should_return_gallery_asset(application):
    article = 'http://xml.zeit.de/centerpage/article_gallery_asset'
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.web.core.centerpage.get_gallery_asset(context)
    assert isinstance(asset, zeit.content.gallery.gallery.Gallery)


def test_get_video_asset_should_return_video_asset(application):
    article = 'http://xml.zeit.de/centerpage/article_video_asset'
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.web.core.centerpage.get_video_asset(
        context)
    assert isinstance(asset, zeit.content.video.video.Video)


def test_default_image_url_should_return_default_image_size(
        application, monkeyreq):
    image_id = \
        'http://xml.zeit.de/centerpage/katzencontent/katzencontent-180x101.jpg'
    image = zeit.cms.interfaces.ICMSContent(image_id)
    image_url = default_image_url(image)
    assert re.search(
        'http://example.com/centerpage/katzencontent/'
        'bitblt-.*-.*/katzencontent-180x101.jpg',
        image_url)


def test_default_image_url_should_return_available_image_size(
        application, monkeyreq):
    image_id = \
        'http://xml.zeit.de/centerpage/katzencontent/katzencontent-180x101.jpg'
    image = zeit.cms.interfaces.ICMSContent(image_id)
    image_url = default_image_url(image)
    assert re.search(
        'http://example.com/centerpage/katzencontent/'
        'bitblt-.*-.*/katzencontent-180x101.jpg',
        image_url)


def test_default_image_url_should_return_none_when_no_unique_id_is_given(
        application, monkeyreq):
    assert default_image_url(mock.Mock()) is None


def test_default_teaser_should_return_default_teaser_image(application):
    cp = 'http://xml.zeit.de/centerpage/lebensart'
    cp_context = zeit.cms.interfaces.ICMSContent(cp)
    teaser_block = cp_context['lead'][0]
    article = 'http://xml.zeit.de/centerpage/article_image_asset'
    article_context = zeit.cms.interfaces.ICMSContent(article)
    teaser_img = get_teaser_image(teaser_block, article_context)
    assert zeit.web.core.interfaces.ITeaserImage.providedBy(teaser_img)


def test_teaser_image_should_be_created_from_imagegroup_and_image(application):
    import zeit.cms.interfaces
    img = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/centerpage/'
                                          'katzencontent/katzencontent'
                                          '-148x84.jpg')
    imgrp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/centerpage/'
                                            'katzencontent/')
    teaser_image = getMultiAdapter(
        (imgrp, img),
        zeit.web.core.interfaces.ITeaserImage)

    assert teaser_image.caption == 'Die ist der image sub text '
    assert teaser_image.src == img.uniqueId
    assert teaser_image.alt == 'Die ist der Alttest'
    assert teaser_image.title == 'Katze!'


def test_get_reaches_from_centerpage_view(application, dummy_request):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo')
    view = zeit.web.magazin.view_centerpage.CenterpageLegacy(cp, dummy_request)

    buzz = view.area_buzz

    buzz_views = buzz[0]
    buzz_facebook = buzz[1]
    buzz_comments = buzz[2]

    assert buzz_views[0] == 'views'
    assert buzz_facebook[0] == 'facebook'
    assert buzz_comments[0] == 'comments'

    assert len(buzz_views[1]) == 3
    assert len(buzz_facebook[1]) == 3
    assert len(buzz_comments[1]) == 3


def test_centerpages_produces_no_error(testbrowser):
    browser = testbrowser('/zeit-magazin/test-cp/test-cp-zmo')
    assert '<div class="page-wrap">' in browser.contents
    browser = testbrowser('/zeit-magazin/test-cp/test-cp-zmo-2')
    assert '<div class="page-wrap">' in browser.contents
    browser = testbrowser('/zeit-magazin/test-cp/test-cp-zmo-3')
    assert '<div class="page-wrap">' in browser.contents
    browser = testbrowser('/zeit-magazin/test-cp/test-cp-zmo-4')
    assert '<div class="page-wrap">' in browser.contents
    browser = testbrowser('/zeit-magazin/test-cp/with-teaserbar')
    assert '<div class="page-wrap">' in browser.contents
    browser = testbrowser('/centerpage/cp_with_image_lead')
    assert '<div class="page-wrap">' in browser.contents
    browser = testbrowser('/centerpage/cp_with_video_lead')
    assert '<div class="page-wrap">' in browser.contents
    browser = testbrowser('/centerpage/lebensart')
    assert '<div class="page-wrap">' in browser.contents
    browser = testbrowser('/centerpage/lebensart-2')
    assert '<div class="page-wrap">' in browser.contents


def test_cp_lead_should_have_correct_first_block(application):
    cp = 'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo-2'
    cp_context = zeit.cms.interfaces.ICMSContent(cp)
    cp_view = zeit.web.magazin.view_centerpage.CenterpageLegacy(
        cp_context, mock.Mock())
    lead1_first_block = (
        'http://block.vivi.zeit.de/http://xml.zeit.de/'
        'zeit-magazin/test-cp/test-cp-zmo-2#body/feature/lead/id-f8f46488'
        '-75ea-46f4-aaff-7654b4e1c805')
    lead1_last_block = (
        'http://block.vivi.zeit.de/http://xml.zeit.de/'
        'zeit-magazin/test-cp/test-cp-zmo-2#body/feature/lead/id-eae7'
        'c703-98e9-491a-a30d-c1c5cebd2371')
    assert lead1_first_block == cp_view.area_lead_1[0].uniqueId
    assert lead1_last_block == cp_view.area_lead_1[3].uniqueId


def test_cp_lead_should_have_correct_second_block(application):
    cp = 'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo-2'
    cp_context = zeit.cms.interfaces.ICMSContent(cp)
    cp_view = zeit.web.magazin.view_centerpage.CenterpageLegacy(
        cp_context, mock.Mock())
    lead2_first_block = (
        'http://block.vivi.zeit.de/http://xml.zeit.de/'
        'zeit-magazin/test-cp/test-cp-zmo-2#body/feature/lead/id-cc6bbea3-'
        '1337-42f5-8fe1-01c9c4476600')
    lead2_last_block = (
        'http://block.vivi.zeit.de/http://xml.zeit.de/'
        'zeit-magazin/test-cp/test-cp-zmo-2#body/feature/lead/id-f8f46488'
        '-75ea-46f4-aaff-7654b4e1c805')
    assert lead2_first_block == cp_view.area_lead_2[0].uniqueId
    assert lead2_last_block == cp_view.area_lead_2[1].uniqueId


def test_cp_lead_should_have_no_blocks(application):
    cp = 'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo'
    cp_context = zeit.cms.interfaces.ICMSContent(cp)
    cp_view = zeit.web.magazin.view_centerpage.CenterpageLegacy(
        cp_context, mock.Mock())
    lead_first_block = (
        'http://block.vivi.zeit.de/http://xml.zeit.de/zeit-mag'
        'azin/test-cp/test-cp-zmo#body/feature/lead/id-f8f46488-75ea-46f4-'
        'aaff-7654b4e1c805')
    lead_last_block = (
        'http://block.vivi.zeit.de/http://xml.zeit.de/'
        'zeit-magazin/test-cp/test-cp-zmo#body/feature/lead/id-48962e5e'
        '-cdbe-4148-a12c-17724cd0e96b')
    assert lead_first_block == cp_view.area_lead_1[0].uniqueId
    assert lead_last_block == cp_view.area_lead_1[3].uniqueId


def test_cp_informatives_should_have_correct_first_block(application):
    cp = 'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo-2'
    cp_context = zeit.cms.interfaces.ICMSContent(cp)
    cp_view = zeit.web.magazin.view_centerpage.CenterpageLegacy(
        cp_context, mock.Mock())
    informatives1_first_block = (
        'http://block.vivi.zeit.de/http://xml.zeit.de'
        '/zeit-magazin/test-cp/test-cp-zmo-2#body/feature/informatives/'
        'id-3d2116f6-96dd-4556-81f7-d7d0a40435e5')
    informatives1_last_block = (
        'http://block.vivi.zeit.de/'
        'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo-2'
        '#body/feature/informatives/id-bff224c9-088e-40d4-987d-9d986de804bd')

    assert informatives1_first_block == cp_view.area_informatives_1[0].uniqueId
    assert informatives1_last_block == cp_view.area_informatives_1[1].uniqueId


def test_cp_informatives_should_have_correct_second_block(application):
    cp = 'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo-2'
    cp_context = zeit.cms.interfaces.ICMSContent(cp)
    cp_view = zeit.web.magazin.view_centerpage.CenterpageLegacy(
        cp_context, mock.Mock())
    informatives2_first_block = (
        'http://block.vivi.zeit.de/http://xml.zeit.de'
        '/zeit-magazin/test-cp/test-cp-zmo-2#body/feature/informatives/id-edc'
        '55a53-7cab-4bbc-a31d-1cf20afe5d9d')
    informatives2_last_block = (
        'http://block.vivi.zeit.de/'
        'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo-2'
        '#body/feature/informatives/id-edc55a53-7cab-4bbc-a31d-'
        '1cf20afe5d9ddshjdsjkdsjk')

    assert informatives2_first_block == cp_view.area_informatives_2[0].uniqueId
    assert informatives2_last_block == cp_view.area_informatives_2[1].uniqueId


def test_cp_informatives_should_have_no_blocks(application):
    cp = 'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo'
    cp_context = zeit.cms.interfaces.ICMSContent(cp)
    cp_view = zeit.web.magazin.view_centerpage.CenterpageLegacy(
        cp_context, mock.Mock())
    informatives_first_block = (
        'http://block.vivi.zeit.de/'
        'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo'
        '#body/feature/informatives/id-3d2116f6-96dd-4556-81f7-d7d0a40435e5')
    informatives_last_block = (
        'http://block.vivi.zeit.de/'
        'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo'
        '#body/feature/informatives/id-edc55a53-7cab-4bbc-a31d-1cf20afe5d9d')

    assert informatives_first_block == cp_view.area_informatives_1[0].uniqueId
    assert informatives_last_block == cp_view.area_informatives_1[2].uniqueId


def test_cp_teaser_should_have_comment_count(
        mockserver_factory, testbrowser):
    cp_counts = """<?xml version="1.0" encoding="UTF-8"?>
    <nodes>
         <node comment_count="129"
               url="/zeit-magazin/test-cp/essen-geniessen-spargel-lamm"/>
    </nodes>
    """
    mockserver_factory(cp_counts)
    browser = testbrowser('/zeit-magazin/test-cp/test-cp-zmo')
    counts = browser.cssselect(
        'span.cp_comment__count__wrap.icon-comments-count')
    assert int(counts[0].text) == 129


def test_centerpage_should_have_monothematic_block(application):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo')
    view = zeit.web.magazin.view_centerpage.CenterpageLegacy(cp, mock.Mock())
    assert len(view.monothematic_block) == 6


def test_centerpage_should_have_no_monothematic_block(application):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/centerpage/lebensart')
    view = zeit.web.magazin.view_centerpage.CenterpageLegacy(cp, mock.Mock())
    assert view.monothematic_block is None


def test_default_asset_for_teaser_lead(testbrowser):
    browser = testbrowser('/zeit-magazin/test-cp/asset-test-1')
    img = browser.cssselect('div.cp_leader--full .cp_leader__asset img')[0]
    assert 'teaser_image-zmo-landscape-large.jpg' in img.attrib.get('src')


def test_default_asset_for_teaser_buttons(testbrowser):
    browser = testbrowser('/zeit-magazin/test-cp/asset-test-1')
    img = browser.cssselect('div.cp_button__image img')[0]
    assert 'teaser_image-zmo-landscape-small.jpg' in img.attrib.get('src')


def test_default_asset_for_teaser_buttons_large(testbrowser):
    browser = testbrowser('/zeit-magazin/test-cp/asset-test-1')
    img = browser.cssselect('div.cp_button--large .cp_button__image img')[0]
    assert 'teaser_image-zmo-landscape-large.jpg' in img.attrib.get('src')


def test_default_asset_for_teaser_gallery(testbrowser):
    browser = testbrowser('/zeit-magazin/test-cp/asset-test-1')
    img = browser.cssselect('div.cp_button--gallery a div img')[0]
    assert 'teaser_image-zmo-upright.jpg' in img.attrib.get('src')


def test_cp_has_gallery_icon_for_gallery_upright_teaser(testbrowser):
    browser = testbrowser('/zeit-magazin/test-cp/test-cp-zmo-2')
    icon = browser.cssselect(
        'div.cp_button--gallery .cp_button__title__wrap a span')[0]
    assert 'icon-galerie-icon-white' in icon.attrib.get('class')


def test_cp_has_no_gallery_icon_for_gallery_upright_teaser(testbrowser):
    browser = testbrowser('/zeit-magazin/test-cp/test-cp-zmo-2')
    icon = browser.cssselect(
        'div.cp_button--gallery .cp_button__title__wrap a span')
    assert len(icon) == 1


def test_cp_has_no_gallery_icon_for_gallery_type_product(
        testbrowser, workingcopy):
    gallery = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/galerien/fs-desktop-schreibtisch-computer')
    with checked_out(gallery) as co:
        co.type = u'zmo-product'
    browser = testbrowser('/zeit-magazin/test-cp/test-cp-zmo-2')
    icon = browser.cssselect(
        'div.cp_button--gallery .cp_button__title__wrap a span')
    assert len(icon) == 0


def test_print_cover_teaser_should_have_modifier(testbrowser):
    browser = testbrowser('/zeit-magazin/index')
    format = browser.cssselect(
        '.cp_button.cp_button--cover')
    assert len(format) == 1


def test_print_cover_teaser_should_have_supertitle(testbrowser):
    browser = testbrowser('/zeit-magazin/index')
    supertitle = browser.cssselect(
        'a[href$="/artikel/02"] h2 .cp_button__supertitle')
    assert len(supertitle) == 1


def test_print_cover_teaser_should_not_have_subtitle(testbrowser):
    browser = testbrowser('/zeit-magazin/index')
    subtitle = browser.cssselect(
        'a[href$="/artikel/02"] h2 .cp_button__subtitle')
    assert len(subtitle) == 0


def test_homepage_indentifies_itself_as_homepage(application):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/index')
    view = zeit.web.magazin.view_centerpage.CenterpageLegacy(cp, mock.Mock())
    assert view.is_hp is True
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-large-teaser')
    view = zeit.web.magazin.view_centerpage.CenterpageLegacy(cp, mock.Mock())
    assert view.is_hp is False


def test_wrapped_features_are_triggered(testbrowser):
    browser = testbrowser('/zeit-magazin/index')
    assert browser.cssselect('nav.main-nav')

    browser = testbrowser('/zeit-magazin/index?app-content')
    assert not browser.cssselect('nav.main-nav')
    assert browser.cssselect('body[data-is-wrapped="true"]')


def test_cp_does_not_render_image_if_expired(testbrowser):
    with mock.patch('zeit.web.core.image.is_image_expired') as expired:
        expired.return_value = True
        browser = testbrowser('/centerpage/lebensart')
    assert not browser.cssselect('.cp_leader__asset--dark')
