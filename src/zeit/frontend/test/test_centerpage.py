# -*- coding: utf-8 -*-
import re

import mock
import pyramid.threadlocal
import pytest
from zope.component import getMultiAdapter

import zeit.cms.interfaces
import zeit.content.gallery.gallery

from zeit.frontend.template import create_image_url
from zeit.frontend.template import default_image_url
from zeit.frontend.template import get_teaser_image
from zeit.frontend.template import get_teaser_template
from zeit.frontend.test import Browser
import zeit.frontend.centerpage
import zeit.frontend.view_centerpage


@pytest.fixture
def monkeyreq(monkeypatch):
    def request():
        m = mock.Mock()
        m.route_url = lambda x: "http://example.com/"
        return m

    monkeypatch.setattr(pyramid.threadlocal, "get_current_request", request)


def test_homepage_should_have_buzz_module_centerpage_should_not(
        testserver):
    browser = Browser('%s/zeit-magazin/index' % testserver.url)
    assert '<div class="cp_buzz">' in browser.contents
    browser = Browser('%s/centerpage/lebensart' % testserver.url)
    assert '<div class="cp_buzz">' not in browser.contents

# commented out for first launch (as)
# def test_centerpage_should_have_pagetitle_in_body_but_hp_not(
#         selenium_driver, testserver):
#     driver = selenium_driver
#     driver.get('%s/zeit-magazin/index' % testserver.url)
#     assert len(driver.find_elements_by_css_selector('.cp_title')) == 0
#     driver.get('%s/centerpage/lebensart' % testserver.url)
#     pagetitle_in_body = driver.find_elements_by_css_selector('.cp_title')
#     assert pagetitle_in_body[0].text.strip() == "ZMO"


def test_centerpage_should_have_correct_page_title(testserver):
    browser = Browser('%s/centerpage/lebensart' % testserver.url)
    assert '<title>ZMO CP: ZMO</title>' in browser.contents


def test_centerpage_should_have_correct_seo_title(testserver):
    browser = Browser('%s/centerpage/lebensart-2' % testserver.url)
    assert '<title>SEO title</title>' in browser.contents


def test_centerpage_should_have_page_meta_description(testserver):
    browser = Browser('%s/centerpage/lebensart' % testserver.url)
    assert '<meta name="description" content="ZMO CP">' in browser.contents


def test_centerpage_should_have_seo_description(testserver):
    browser = Browser('%s/centerpage/lebensart-2' % testserver.url)
    assert '<meta name="description" content="SEO description">' \
        in browser.contents


def test_centerpage_should_have_default_keywords(testserver):
    # Default means ressort and sub ressort respectively
    browser = Browser('%s/centerpage/lebensart-2' % testserver.url)
    assert '<meta name="keywords" content="Lebensart, mode-design">' \
        in browser.contents


def test_centerpage_should_have_page_meta_keywords(testserver):
    browser = Browser('%s/centerpage/lebensart' % testserver.url)
    assert '<meta name="keywords" content="Pinguin">' \
        in browser.contents


def test_centerpage_should_have_page_meta_robots_information(
        browser, testserver):
    # SEO robots information is given
    browser = Browser('%s/centerpage/lebensart' % testserver.url)
    meta_robots = browser.document.xpath('//meta[@name="robots"]/@content')
    assert 'my, personal, seo, robots, information' in meta_robots
    # No SEO robots information is given
    browser = Browser('%s/zeit-magazin/index' % testserver.url)
    meta_robots = browser.document.xpath('//meta[@name="robots"]/@content')
    assert 'index,follow,noodp,noydir,noarchive' in meta_robots


def test_get_teaser_template_should_produce_correct_combinations():
    should = [
        'templates/inc/teaser/teaser_lead_article_video.html',
        'templates/inc/teaser/teaser_lead_article_default.html',
        'templates/inc/teaser/teaser_lead_default_video.html',
        'templates/inc/teaser/teaser_lead_default_default.html',
        'templates/inc/teaser/teaser_default_article_video.html',
        'templates/inc/teaser/teaser_default_article_default.html',
        'templates/inc/teaser/teaser_default_default_video.html',
        'templates/inc/teaser/teaser_default_default_default.html']
    result = get_teaser_template('lead', 'article', 'video')
    assert result == should
    should = [
        'templates/inc/teaser/teaser_lead_article_video.html',
        'templates/inc/teaser/teaser_lead_article_gallery.html',
        'templates/inc/teaser/teaser_lead_article_imagegroup.html',
        'templates/inc/teaser/teaser_lead_article_default.html',
        'templates/inc/teaser/teaser_lead_default_video.html',
        'templates/inc/teaser/teaser_lead_default_gallery.html',
        'templates/inc/teaser/teaser_lead_default_imagegroup.html',
        'templates/inc/teaser/teaser_lead_default_default.html',
        'templates/inc/teaser/teaser_default_article_video.html',
        'templates/inc/teaser/teaser_default_article_gallery.html',
        'templates/inc/teaser/teaser_default_article_imagegroup.html',
        'templates/inc/teaser/teaser_default_article_default.html',
        'templates/inc/teaser/teaser_default_default_video.html',
        'templates/inc/teaser/teaser_default_default_gallery.html',
        'templates/inc/teaser/teaser_default_default_imagegroup.html',
        'templates/inc/teaser/teaser_default_default_default.html']
    assets = ('video', 'gallery', 'imagegroup')
    result = get_teaser_template('lead', 'article', assets)
    assert result == should


def test_autoselected_asset_from_cp_teaser_should_be_a_gallery(testserver):
    article = 'http://xml.zeit.de/centerpage/article_gallery_asset'
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.frontend.centerpage.auto_select_asset(context)
    assert isinstance(asset, zeit.content.gallery.gallery.Gallery)


def test_autoselected_asset_from_cp_teaser_should_be_an_image(testserver):
    article = 'http://xml.zeit.de/centerpage/article_image_asset'
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.frontend.centerpage.auto_select_asset(context)
    assert isinstance(asset, zeit.content.image.imagegroup.ImageGroup)


def test_autoselected_asset_from_cp_teaser_should_be_a_video(testserver):
    article = 'http://xml.zeit.de/centerpage/article_video_asset'
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.frontend.centerpage.auto_select_asset(context)
    assert isinstance(asset, zeit.content.video.video.Video)


def test_autoselected_asset_from_cp_teaser_should_be_a_video_list(testserver):
    article = 'http://xml.zeit.de/centerpage/article_video_asset_2'
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.frontend.centerpage.auto_select_asset(context)
    assert isinstance(asset[0], zeit.content.video.video.Video)
    assert isinstance(asset[1], zeit.content.video.video.Video)


def test_cp_has_lead_area(testserver):
    browser = Browser('%s/centerpage/lebensart' % testserver.url)
    assert '<div class="cp_lead__wrap">' in browser.contents


def test_cp_has_informatives_area(testserver):
    browser = Browser('%s/centerpage/lebensart' % testserver.url)
    assert '<div class="cp_informatives__wrap">' in browser.contents


def test_cp_lead_areas_are_available(application):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/centerpage/lebensart')
    view = zeit.frontend.view_centerpage.Centerpage(cp, mock.Mock())
    assert len(view.area_lead)


def test_cp_leadteaser_has_expected_structure(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/lebensart' % testserver.url)
    wrap = driver.find_elements_by_css_selector(".cp_leader")
    assert len(wrap) != 0
    for element in wrap:
        text_wrap = element.find_elements_by_css_selector(
            ".cp_leader__title__wrap--dark")
        link_wrap = element.find_elements_by_tag_name(
            "a")
        image_wrap = element.find_elements_by_css_selector(
            ".cp_leader__asset--dark")
        assert len(text_wrap) != 0
        assert len(link_wrap) == 2
        assert len(image_wrap) != 0


def test_cp_leadteaser_has_expected_text_content(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/lebensart' % testserver.url)
    wrap = driver.find_elements_by_css_selector(
        ".cp_leader__title__wrap--dark")
    assert len(wrap) != 0
    for element in wrap:
        supertitle = element.find_element_by_css_selector(
            ".cp_leader__supertitle")
        title = element.find_element_by_css_selector(".cp_leader__title")
        subtitle = element.find_element_by_css_selector(".cp_leader__subtitle")
        assert unicode(supertitle.text) == u'Article Image Asset Spitzmarke'
        assert unicode(title.text) == u'Article Image Asset Titel'
        assert unicode(subtitle.text) == u'Dies k\u00F6nnte'\
            ' z.B. lorem ipsum sein.'\
            ' Oder was anderes nicht ganz so langweiliges,'\
            ' zum Katzenbild passen.'


def test_cp_leadteaser_has_expected_img_content(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/lebensart' % testserver.url)
    wrap = driver.find_elements_by_css_selector(
        ".cp_leader__asset--dark")
    assert len(wrap) != 0
    for element in wrap:
        img = element.find_element_by_tag_name(
            "img")
        assert re.search('http://.*/centerpage/katzencontent/' +
                         'bitblt-.*/' +
                         'katzencontent-zmo-square-large.jpg',
                         img.get_attribute("src"))
        assert img.get_attribute("alt") == 'Die ist der Alttest'
        assert img.get_attribute("title") == 'Katze!'


def test_cp_leadteaser_has_expected_links(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/lebensart' % testserver.url)
    wrap = driver.find_elements_by_css_selector(".cp_leader")
    assert len(wrap) != 0
    for element in wrap:
        link_wrap = element.find_elements_by_tag_name("a")
        assert len(link_wrap) == 2
        for link in link_wrap:
            assert link.get_attribute("href") == 'http://'\
                'localhost:6543/centerpage/article_image_asset'


def test_cp_img_button_has_expected_structure(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/lebensart' % testserver.url)
    wrap = driver.find_elements_by_css_selector(".cp_button")
    assert len(wrap) != 0
    for element in wrap:
        text_wrap = element.find_elements_by_css_selector(
            ".cp_button__title__wrap")
        link_wrap = element.find_elements_by_tag_name(
            "a")
        assert len(text_wrap) != 0
        assert len(link_wrap) >= 1


def test_cp_img_button_has_expected_img_content(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/lebensart' % testserver.url)
    wrap = driver.find_elements_by_css_selector(
        ".cp_lead__wrap .cp_button__image")
    assert len(wrap) != 0
    for element in wrap:
        img = element.find_element_by_tag_name(
            "img")

        image_pattern = \
            'http://.*/centerpage/katzencontent/'\
            'bitblt-.*'\
            '/katzencontent-zmo-landscape-small.jpg'
        assert re.search(image_pattern, img.get_attribute("src"))
        assert img.get_attribute("alt") == 'Die ist der Alttest'
        assert img.get_attribute("title") == 'Katze!'


def test_cp_button_has_expected_structure(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-magazin/test-cp/test-cp-zmo' % testserver.url)
    wrap = driver.find_elements_by_css_selector(".cp_button--small")
    assert len(wrap) != 0
    for element in wrap:
        assert element.find_elements_by_xpath("a")
        assert element.find_elements_by_xpath(
            "a/div/img[@class=' figure__media']")
        assert element.find_elements_by_css_selector(
            ".cp_button__title__wrap")
        assert element.find_elements_by_xpath("header/a/h2")
        assert element.find_elements_by_xpath(
            "header/a/span[@class='cp_button__subtitle']")


def test_cp_button_has_expected_text_content(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/lebensart' % testserver.url)
    wrap = driver.find_elements_by_css_selector(
        ".cp_button--small")
    assert len(wrap) != 0
    for element in wrap:
        supertitle = element.find_element_by_css_selector(
            ".cp_button__supertitle")
        title = element.find_element_by_css_selector(".cp_button__title")
        subtitle = element.find_element_by_css_selector(
            ".cp_button__subtitle")
        assert unicode(supertitle.text) == u'Article Image Asset Spitzmarke'
        assert unicode(title.text) == u'Article Image Asset Titel'
        assert unicode(subtitle.text) == u'Dies k\u00F6nnte'\
            ' z.B. lorem ipsum sein.'\
            ' Oder was anderes nicht ganz so langweiliges,'\
            ' zum Katzenbild passen.'


def test_cp_button_has_expected_links(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/lebensart' % testserver.url)
    wrap = driver.find_elements_by_css_selector(".cp_button--small")
    assert len(wrap) != 0
    for element in wrap:
        link_wrap = element.find_elements_by_tag_name("a")
        assert len(link_wrap) != 0
        for link in link_wrap:
            assert link.get_attribute("href") == 'http://'\
                'localhost:6543/centerpage/article_image_asset'


def test_cp_large_photo_button_has_expected_structure(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-magazin/test-cp/test-cp-zmo-2' % testserver.url)
    wrap = driver.find_elements_by_css_selector(".cp_button--large-photo")
    assert len(wrap) != 0
    for element in wrap:
        text_wrap = element.find_elements_by_css_selector(
            ".cp_button__title__wrap")
        link_wrap = element.find_elements_by_tag_name(
            "a")
        assert len(text_wrap) != 0
        assert len(link_wrap) == 2


def test_cp_large_photo_button_has_expected_text_content(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-magazin/test-cp/test-cp-zmo-2' % testserver.url)
    wrap = driver.find_elements_by_css_selector(
        ".cp_button--large-photo")
    assert len(wrap) != 0
    for element in wrap:
        supertitle = element.find_element_by_css_selector(
            ".cp_button__supertitle")
        title = element.find_element_by_css_selector(
            ".cp_button__title")
        assert unicode(supertitle.text) == u'Serie Gesellschaftskritik'
        assert unicode(title.text) == u'\u00DCBER SCHLECHTE LAUNE'


def test_cp_large_photo_button_has_expected_links(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-magazin/test-cp/test-cp-zmo-2' % testserver.url)
    wrap = driver.find_elements_by_css_selector(".cp_button--large-photo")
    assert len(wrap) != 0
    for element in wrap:
        link_wrap = element.find_elements_by_tag_name("a")
        assert len(link_wrap) != 0
        for link in link_wrap:
            assert re.search(
                'http://.*/zeit-magazin/test-cp/' +
                'gesellschaftskritik-grumpy-cat',
                link.get_attribute("href"))


def test_cp_gallery_teaser_has_expected_structure(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/lebensart' % testserver.url)
    wrap = driver.find_elements_by_css_selector(".cp_button--gallery")
    assert len(wrap) != 0
    for element in wrap:
        text_wrap = element.find_elements_by_css_selector(
            ".cp_button__title__wrap")
        link_wrap = element.find_elements_by_tag_name(
            "a")
        image_wrap = element.find_elements_by_css_selector(
            ".scaled-image")
        assert len(text_wrap) != 0
        assert len(link_wrap) == 2
        assert len(image_wrap) != 0


def test_cp_gallery_teaser_has_expected_text_content(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/lebensart' % testserver.url)
    wrap = driver.find_elements_by_css_selector(
        ".cp_button--gallery")
    assert len(wrap) != 0
    for element in wrap:
        supertitle = element.find_element_by_css_selector(
            ".cp_button__supertitle")
        title = element.find_element_by_css_selector(
            ".cp_button__title")
        assert unicode(supertitle.text) == u'Article Image Asset Spitzmarke'
        assert unicode(title.text) == u'Article Image Asset Titel'


def test_gallery_teaser_has_expected_img_content(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/lebensart' % testserver.url)
    wrap = driver.find_elements_by_css_selector(
        ".cp_button--gallery")
    assert len(wrap) != 0
    for element in wrap:
        img = element.find_element_by_tag_name(
            "img")
        assert re.search('http://.*/centerpage/katzencontent/' +
                         'bitblt-.*/' +
                         'katzencontent-zmo-upright.jpg',
                         img.get_attribute("src"))
        assert img.get_attribute("alt") == 'Die ist der Alttest'
        assert img.get_attribute("title") == 'Katze!'


def test_cp_should_have_informatives_ad_at_3rd_place(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-magazin/test-cp/test-cp-zmo' % testserver.url)
    wrap = driver.find_elements_by_css_selector(
        ".cp_informatives__wrap")
    assert len(wrap) != 0
    elements = wrap[0].find_elements_by_xpath("div")
    add = elements[2].get_attribute("class")
    assert add == 'cp_button--ad'
    mr = elements[2].find_element_by_css_selector(
        "#iqadtile7").get_attribute("class")
    assert mr == "ad__tile_7 ad__on__centerpage ad__width_300 ad__min__768"


def test_cp_with_video_lead_has_correct_markup(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/cp_with_video_lead' % testserver.url)
    wrap = driver.find_elements_by_css_selector(".cp_leader--full")
    assert len(wrap) != 0
    for teaser in wrap:
        vid_wrap = teaser.find_element_by_class_name("cp_leader__asset--dark")
        vid = teaser.find_element_by_tag_name("video")
        img = teaser.find_element_by_tag_name("img")
        title_wrap = teaser.find_element_by_tag_name("header")
        h2 = teaser.find_element_by_tag_name("h2")
        a = teaser.find_elements_by_tag_name("a")
        title = teaser.find_elements_by_class_name("cp_leader__title")
        subtitle = teaser.find_elements_by_class_name("cp_leader__subtitle")
        source1 = \
            teaser.find_element_by_xpath('//source[1]').get_attribute("src")
        source2 = \
            teaser.find_element_by_xpath('//source[2]').get_attribute("src")

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
        assert 'true' == unicode(vid.get_attribute("autoplay"))
        assert 'video--fallback ' == unicode(img.get_attribute("class"))
        assert 'cp_leader__title__wrap'\
            ' cp_leader__title__wrap--dark' == \
            unicode(title_wrap.get_attribute("class"))
        assert len(title) == 1
        assert len(subtitle) == 1

        # content
        assert '3035864892001' == \
            unicode(vid_wrap.get_attribute("data-backgroundvideo"))
        assert 'Es leben die Skispringenden Sportredakteure!' == \
            unicode(subtitle[0].text)
        assert src_img == unicode(img.get_attribute("src"))
        assert u'und der Titel dazu' == unicode(title[0].text)
        assert src1_val == unicode(source1)
        assert src2_val == unicode(source2)

        # links
        assert len(a) == 2
        for link in a:
            assert link.get_attribute("href") == 'http://localhost'\
                ':6543/centerpage/article_video_asset'


def test_cp_with_image_lead_has_correct_markup(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/cp_with_image_lead' % testserver.url)
    wrap = driver.find_elements_by_css_selector(".cp_leader--full")
    assert len(wrap) != 0
    for teaser in wrap:
        img_wrap = teaser.find_elements_by_class_name("cp_leader__asset--dark")
        img = teaser.find_element_by_tag_name("img")
        title_wrap = teaser.find_elements_by_tag_name("header")
        h2 = teaser.find_element_by_tag_name("h2")
        a = teaser.find_elements_by_tag_name("a")
        title = teaser.find_elements_by_class_name("cp_leader__title")
        subtitle = teaser.find_elements_by_class_name("cp_leader__subtitle")
        image_pattern = \
            'http://.*/centerpage/katzencontent/'\
            'bitblt-.*'\
            '/katzencontent-zmo-landscape-large.jpg'

        # structure
        assert len(img_wrap) != 0
        assert len(title_wrap) != 0

        assert re.search(image_pattern, img.get_attribute("src"))
        assert unicode(title[0].text) == u'Article Image Asset Titel'
        assert unicode(subtitle[0].text) == u'Dies k\u00F6nnte'\
            ' z.B. lorem ipsum sein.'\
            ' Oder was anderes nicht ganz so langweiliges,'\
            ' zum Katzenbild passen.'
        assert img.get_attribute("alt") == 'Die ist der Alttest'
        assert img.get_attribute("title") == 'Katze!'

        # links
        assert len(a) == 2
        for link in a:
            assert link.get_attribute("href") == 'http://localhost'\
                ':6543/centerpage/article_image_asset'


def test_lead_full_light_version_is_working(testserver):
    browser = Browser('%s/zeit-magazin/test-cp/test-cp-zmo-2' % testserver.url)
    assert '<div class="cp_leader cp_leader--full">' in browser.contents
    assert '<div class="scaled-image is-pixelperfect cp_leader__asset'\
        ' cp_leader__asset--light" data-wrap=".cp_leader">' in browser.contents


def test_lead_leader_light_version_is_working(testserver):
    browser = Browser('%s/centerpage/lebensart-2' % testserver.url)
    assert '<div class="scaled-image is-pixelperfect '\
        'cp_leader__asset cp_leader__asset--light" '\
        'data-wrap=".cp_leader">' in browser.contents


def test_get_image_asset_should_return_image_asset(testserver):
    article = 'http://xml.zeit.de/centerpage/article_image_asset'
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.frontend.centerpage.get_image_asset(
        context)
    assert isinstance(asset, zeit.content.image.imagegroup.ImageGroup)


def test_get_gallery_asset_should_return_gallery_asset(testserver):
    article = 'http://xml.zeit.de/centerpage/article_gallery_asset'
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.frontend.centerpage.get_gallery_asset(
        context)
    assert isinstance(asset, zeit.content.gallery.gallery.Gallery)


def test_get_video_asset_should_return_video_asset(testserver):
    article = 'http://xml.zeit.de/centerpage/article_video_asset'
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.frontend.centerpage.get_video_asset(
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


def test_default_image_url_should_return_None_when_no_uniqueId_is_given(
        testserver, monkeyreq):
    m = mock.Mock()
    assert default_image_url(m) is None


def test_default_teaser_should_return_default_teaser_image(testserver):
    cp = 'http://xml.zeit.de/centerpage/lebensart'
    cp_context = zeit.cms.interfaces.ICMSContent(cp)
    teaser_block = cp_context['lead'][0]
    article = 'http://xml.zeit.de/centerpage/article_image_asset'
    article_context = zeit.cms.interfaces.ICMSContent(article)
    teaser_img = get_teaser_image(teaser_block, article_context)
    assert zeit.frontend.interfaces.ITeaserImage.providedBy(teaser_img)


def test_teaser_image_url_should_be_created(
        testserver, monkeyreq):
    cp = 'http://xml.zeit.de/centerpage/lebensart'
    cp_context = zeit.cms.interfaces.ICMSContent(cp)
    teaser_block = cp_context['lead'][0]

    article = 'http://xml.zeit.de/centerpage/article_image_asset'
    article_context = zeit.cms.interfaces.ICMSContent(article)

    teaser_image = get_teaser_image(teaser_block, article_context)

    image_url = create_image_url(teaser_block, teaser_image)
    assert re.search(
        "http://example.com/centerpage/katzencontent/"
        "bitblt-.*katzencontent-zmo-square-large.jpg",
        image_url)


def test_teaser_image_should_be_created_from_image_group_and_image(testserver):
    import zeit.cms.interfaces
    img = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/centerpage/'
                                          'katzencontent/katzencontent'
                                          '-148x84.jpg')
    imgrp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/centerpage/'
                                            'katzencontent/')
    teaser_image = getMultiAdapter(
        (imgrp, img),
        zeit.frontend.interfaces.ITeaserImage)

    assert teaser_image.caption == 'Die ist der image sub text '
    assert teaser_image.src == img.uniqueId
    assert teaser_image.attr_alt == 'Die ist der Alttest'
    assert teaser_image.attr_title == 'Katze!'


def test_get_reaches_from_centerpage_view(application, app_settings):
    request = mock.Mock()
    request.registry.settings.community_host = app_settings['community_host']
    request.registry.settings.linkreach_host = app_settings['linkreach_host']
    request.registry.settings.node_comment_statistics = app_settings[
        'node_comment_statistics']

    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo')
    view = zeit.frontend.view_centerpage.Centerpage(cp, request)

    buzz = view.area_buzz
    assert set(buzz.keys()) == {'facebook', 'twitter', 'comments'}
    assert len(buzz['facebook']) == 3
    assert len(buzz['twitter']) == 3
    assert len(buzz['comments']) == 3


def test_centerpages_produces_no_error(testserver):
    browser = Browser('%s/zeit-magazin/test-cp/test-cp-zmo' % testserver.url)
    assert '<div class="page-wrap">' in browser.contents
    browser = Browser('%s/zeit-magazin/test-cp/test-cp-zmo-2' % testserver.url)
    assert '<div class="page-wrap">' in browser.contents
    browser = Browser('%s/zeit-magazin/test-cp/test-cp-zmo-3' % testserver.url)
    assert '<div class="page-wrap">' in browser.contents
    browser = Browser('%s/zeit-magazin/test-cp/test-cp-zmo-4' % testserver.url)
    assert '<div class="page-wrap">' in browser.contents
    browser = Browser(
        '%s/zeit-magazin/test-cp/with-teaserbar' % testserver.url)
    assert '<div class="page-wrap">' in browser.contents
    browser = Browser('%s/centerpage/cp_with_image_lead' % testserver.url)
    assert '<div class="page-wrap">' in browser.contents
    browser = Browser('%s/centerpage/cp_with_video_lead' % testserver.url)
    assert '<div class="page-wrap">' in browser.contents
    browser = Browser('%s/centerpage/lebensart' % testserver.url)
    assert '<div class="page-wrap">' in browser.contents
    browser = Browser('%s/centerpage/lebensart-2' % testserver.url)
    assert '<div class="page-wrap">' in browser.contents


def test_cp_lead_should_have_correct_first_block(application):
    cp = 'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo-2'
    cp_context = zeit.cms.interfaces.ICMSContent(cp)
    cp_view = zeit.frontend.view_centerpage.Centerpage(cp_context, mock.Mock())
    lead1_first_block = 'http://block.vivi.zeit.de/http://xml.zeit.de/'\
        'zeit-magazin/test-cp/test-cp-zmo-2#'\
        'lead/id-f8f46488-75ea-46f4-aaff-7654b4e1c805'
    lead1_last_block = 'http://block.vivi.zeit.de/http://xml.zeit.de/'\
        'zeit-magazin/test-cp/test-cp-zmo-2#lead/'\
        'id-eae7c703-98e9-491a-a30d-c1c5cebd2371'
    assert lead1_first_block == cp_view.area_lead_1[0].uniqueId
    assert lead1_last_block == cp_view.area_lead_1[3].uniqueId


def test_cp_lead_should_have_correct_second_block(application):
    cp = 'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo-2'
    cp_context = zeit.cms.interfaces.ICMSContent(cp)
    cp_view = zeit.frontend.view_centerpage.Centerpage(cp_context, mock.Mock())
    lead2_first_block = 'http://block.vivi.zeit.de/http://xml.zeit.de/'\
        'zeit-magazin/test-cp/test-cp-zmo-2#lead/'\
        'id-cc6bbea3-1337-42f5-8fe1-01c9c4476600'
    lead2_last_block = 'http://block.vivi.zeit.de/http://xml.zeit.de/'\
        'zeit-magazin/test-cp/test-cp-zmo-2#lead/'\
        'id-f8f46488-75ea-46f4-aaff-7654b4e1c805'
    assert lead2_first_block == cp_view.area_lead_2[0].uniqueId
    assert lead2_last_block == cp_view.area_lead_2[1].uniqueId


def test_cp_lead_should_have_no_blocks(application):
    cp = 'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo'
    cp_context = zeit.cms.interfaces.ICMSContent(cp)
    cp_view = zeit.frontend.view_centerpage.Centerpage(cp_context, mock.Mock())
    lead_first_block = 'http://block.vivi.zeit.de/http://xml.zeit.de/'\
        'zeit-magazin/test-cp/test-cp-zmo#lead/'\
        'id-f8f46488-75ea-46f4-aaff-7654b4e1c805'
    lead_last_block = 'http://block.vivi.zeit.de/http://xml.zeit.de/'\
        'zeit-magazin/test-cp/test-cp-zmo#lead/'\
        'id-48962e5e-cdbe-4148-a12c-17724cd0e96b'
    assert lead_first_block == cp_view.area_lead_1[0].uniqueId
    assert lead_last_block == cp_view.area_lead_1[3].uniqueId


def test_cp_informatives_should_have_correct_first_block(application):
    cp = 'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo-2'
    cp_context = zeit.cms.interfaces.ICMSContent(cp)
    cp_view = zeit.frontend.view_centerpage.Centerpage(cp_context, mock.Mock())
    informatives1_first_block = 'http://block.vivi.zeit.de/'\
        'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo-2'\
        '#informatives/id-3d2116f6-96dd-4556-81f7-d7d0a40435e5'
    informatives1_last_block = 'http://block.vivi.zeit.de/'\
        'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo-2'\
        '#informatives/id-bff224c9-088e-40d4-987d-9d986de804bd'

    assert informatives1_first_block == cp_view.area_informatives_1[0].uniqueId
    assert informatives1_last_block == cp_view.area_informatives_1[1].uniqueId


def test_cp_informatives_should_have_correct_second_block(application):
    cp = 'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo-2'
    cp_context = zeit.cms.interfaces.ICMSContent(cp)
    cp_view = zeit.frontend.view_centerpage.Centerpage(cp_context, mock.Mock())
    informatives2_first_block = 'http://block.vivi.zeit.de/'\
        'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo-2'\
        '#informatives/id-edc55a53-7cab-4bbc-a31d-1cf20afe5d9d'
    informatives2_last_block = 'http://block.vivi.zeit.de/'\
        'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo-2'\
        '#informatives/id-3d2116f6-96dd-4556-81f7-d7d0a40435e5'

    assert informatives2_first_block == cp_view.area_informatives_2[0].uniqueId
    assert informatives2_last_block == cp_view.area_informatives_2[1].uniqueId


def test_cp_informatives_should_have_no_blocks(application):
    cp = 'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo'
    cp_context = zeit.cms.interfaces.ICMSContent(cp)
    cp_view = zeit.frontend.view_centerpage.Centerpage(cp_context, mock.Mock())
    informatives_first_block = 'http://block.vivi.zeit.de/'\
        'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo'\
        '#informatives/id-3d2116f6-96dd-4556-81f7-d7d0a40435e5'
    informatives_last_block = 'http://block.vivi.zeit.de/'\
        'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo'\
        '#informatives/id-edc55a53-7cab-4bbc-a31d-1cf20afe5d9d'

    assert informatives_first_block == cp_view.area_informatives_1[0].uniqueId
    assert informatives_last_block == cp_view.area_informatives_1[2].uniqueId


def test_cp_teaser_should_have_comment_count(testserver):
    browser = Browser('%s/zeit-magazin/test-cp/test-cp-zmo' % testserver.url)
    assert '<span class="cp_comment__count__wrap'\
        ' icon-comments-count">22</span>' in browser.contents


def test_centerpage_should_have_monothematic_block(application):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo')
    view = zeit.frontend.view_centerpage.Centerpage(cp, mock.Mock())
    assert len(view.monothematic_block) == 6


def test_centerpage_should_have_no_monothematic_block(application):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/centerpage/lebensart')
    view = zeit.frontend.view_centerpage.Centerpage(cp, mock.Mock())
    assert view.monothematic_block is None


def test_default_asset_for_teaser_lead(testserver):
    browser = Browser('%s/zeit-magazin/test-cp/asset-test-1' % testserver.url)
    img = browser.cssselect('div.cp_leader--full .cp_leader__asset img')[0]
    assert 'teaser_image-zmo-landscape-large.jpg' in img.attrib.get('src')


def test_default_asset_for_teaser_buttons(testserver):
    browser = Browser('%s/zeit-magazin/test-cp/asset-test-1' % testserver.url)
    img = browser.cssselect('div.cp_button__image img')[0]
    assert 'teaser_image-zmo-landscape-small.jpg' in img.attrib.get('src')


def test_default_asset_for_teaser_buttons_large(testserver):
    browser = Browser('%s/zeit-magazin/test-cp/asset-test-1' % testserver.url)
    img = browser.cssselect('div.cp_button--large .cp_button__image img')[0]
    assert 'teaser_image-zmo-landscape-large.jpg' in img.attrib.get('src')


def test_default_asset_for_teaser_gallery(testserver):
    browser = Browser('%s/zeit-magazin/test-cp/asset-test-1' % testserver.url)
    img = browser.cssselect('div.cp_button--gallery a div img')[0]
    assert 'teaser_image-zmo-upright.jpg' in img.attrib.get('src')
