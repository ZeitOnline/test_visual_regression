# -*- coding: utf-8 -*-
import re

from zope.component import getMultiAdapter
import mock
import pyramid.threadlocal
import pytest
import zope.component

from zeit.cms.checkout.helper import checked_out
import zeit.cms.interfaces
import zeit.content.gallery.gallery
import zeit.cms.syndication.feed

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


def test_homepage_should_have_buzz_module_centerpage_should_not(
        testserver, testbrowser):
    browser = testbrowser('%s/zeit-magazin/index' % testserver.url)
    assert '<div class="cp_buzz">' in browser.contents
    browser = testbrowser('%s/centerpage/lebensart' % testserver.url)
    assert '<div class="cp_buzz">' not in browser.contents


def test_centerpage_should_have_default_keywords(testserver, testbrowser):
    # Default means ressort and sub ressort respectively
    browser = testbrowser('%s/centerpage/lebensart-2' % testserver.url)
    assert '<meta name="keywords" content="Lebensart, mode-design">' in (
        browser.contents)


def test_centerpage_should_have_page_meta_keywords(testserver, testbrowser):
    browser = testbrowser('%s/centerpage/lebensart' % testserver.url)
    assert '<meta name="keywords" content="Pinguin">' in (
        browser.contents)


def test_centerpage_should_have_page_meta_robots_information(
        appbrowser, testserver, testbrowser):
    # SEO robots information is given
    browser = testbrowser('%s/centerpage/lebensart' % testserver.url)
    meta_robots = browser.document.xpath('//meta[@name="robots"]/@content')
    assert 'my, personal, seo, robots, information' in meta_robots
    # No SEO robots information is given
    browser = testbrowser('%s/zeit-magazin/index' % testserver.url)
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


def test_autoselected_asset_from_cp_teaser_should_be_a_gallery(
        testserver, testbrowser):
    article = 'http://xml.zeit.de/centerpage/article_gallery_asset'
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.web.core.centerpage.auto_select_asset(context)
    assert isinstance(asset, zeit.content.gallery.gallery.Gallery)


def test_autoselected_asset_from_cp_teaser_should_be_an_image(
        testserver, testbrowser):
    article = 'http://xml.zeit.de/centerpage/article_image_asset'
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.web.core.centerpage.auto_select_asset(context)
    assert isinstance(asset, zeit.content.image.imagegroup.ImageGroup)


def test_autoselected_asset_from_cp_teaser_should_be_a_video(
        testserver, testbrowser):
    article = 'http://xml.zeit.de/centerpage/article_video_asset'
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.web.core.centerpage.auto_select_asset(context)
    assert isinstance(asset, zeit.content.video.video.Video)


def test_autoselected_asset_from_cp_teaser_should_be_a_video_list(
        testserver, testbrowser):
    article = 'http://xml.zeit.de/centerpage/article_video_asset_2'
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.web.core.centerpage.auto_select_asset(context)
    assert isinstance(asset[0], zeit.content.video.video.Video)
    assert isinstance(asset[1], zeit.content.video.video.Video)


def test_cp_has_lead_area(testserver, testbrowser):
    browser = testbrowser('%s/centerpage/lebensart' % testserver.url)
    assert '<div class="cp_lead__wrap">' in browser.contents


def test_cp_has_informatives_area(testserver, testbrowser):
    browser = testbrowser('%s/centerpage/lebensart' % testserver.url)
    assert '<div class="cp_informatives__wrap">' in browser.contents


def test_cp_lead_areas_are_available(application):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/centerpage/lebensart')
    view = zeit.web.magazin.view_centerpage.CenterpageLegacy(cp, mock.Mock())
    assert len(view.area_lead)


def test_get_image_asset_should_return_image_asset(testserver, testbrowser):
    article = 'http://xml.zeit.de/centerpage/article_image_asset'
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.web.core.centerpage.get_image_asset(
        context)
    assert isinstance(asset, zeit.content.image.imagegroup.ImageGroup)


def test_get_gallery_asset_should_return_gallery_asset(
        testserver, testbrowser):
    article = 'http://xml.zeit.de/centerpage/article_gallery_asset'
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.web.core.centerpage.get_gallery_asset(
        context)
    assert isinstance(asset, zeit.content.gallery.gallery.Gallery)


def test_get_video_asset_should_return_video_asset(testserver, testbrowser):
    article = 'http://xml.zeit.de/centerpage/article_video_asset'
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.web.core.centerpage.get_video_asset(
        context)
    assert isinstance(asset, zeit.content.video.video.Video)


def test_default_image_url_should_return_default_image_size(
        testserver, monkeyreq):
    image_id = \
        'http://xml.zeit.de/centerpage/katzencontent/katzencontent-180x101.jpg'
    image = zeit.cms.interfaces.ICMSContent(image_id)
    image_url = default_image_url(image)
    assert re.search(
        'http://example.com/centerpage/katzencontent/'
        'bitblt-.*-.*/katzencontent-180x101.jpg',
        image_url)


def test_default_image_url_should_return_available_image_size(
        testserver, monkeyreq):
    image_id = \
        'http://xml.zeit.de/centerpage/katzencontent/katzencontent-180x101.jpg'
    image = zeit.cms.interfaces.ICMSContent(image_id)
    image_url = default_image_url(image)
    assert re.search(
        'http://example.com/centerpage/katzencontent/'
        'bitblt-.*-.*/katzencontent-180x101.jpg',
        image_url)


def test_default_image_url_should_return_none_when_no_unique_id_is_given(
        testserver, monkeyreq):
    assert default_image_url(mock.Mock()) is None


def test_default_teaser_should_return_default_teaser_image(
        application, testserver, testbrowser):
    cp = 'http://xml.zeit.de/centerpage/lebensart'
    cp_context = zeit.cms.interfaces.ICMSContent(cp)
    teaser_block = cp_context['lead'][0]
    article = 'http://xml.zeit.de/centerpage/article_image_asset'
    article_context = zeit.cms.interfaces.ICMSContent(article)
    teaser_img = get_teaser_image(teaser_block, article_context)
    assert zeit.web.core.interfaces.ITeaserImage.providedBy(teaser_img)


def test_teaser_image_should_be_created_from_image_group_and_image(
        testserver, testbrowser):
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


def test_get_reaches_from_centerpage_view(application):
    settings = zope.component.queryUtility(zeit.web.core.interfaces.ISettings)
    request = mock.Mock()
    request.registry.settings.community_host = settings['community_host']
    request.registry.settings.linkreach_host = settings['linkreach_host']
    request.registry.settings.node_comment_statistics = settings[
        'node_comment_statistics']

    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo')
    view = zeit.web.magazin.view_centerpage.CenterpageLegacy(cp, request)

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


def test_homepage_indentifies_itself_as_homepage(testserver):
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
