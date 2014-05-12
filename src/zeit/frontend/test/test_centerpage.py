from zeit.frontend import view_centerpage
from zeit.frontend.jinja import create_image_url
from zeit.frontend.jinja import default_image_url
from zeit.frontend.jinja import most_sufficient_teaser_image
from zeit.frontend.jinja import most_sufficient_teaser_tpl
from zope.component import getMultiAdapter
import mock
import pyramid.threadlocal
import pytest
import re
import zeit.cms.interfaces
import zeit.content.gallery.gallery


@pytest.fixture
def monkeyreq(monkeypatch):
    def request():
        m = mock.Mock()
        m.route_url = lambda x: "http://example.com/"
        return m

    monkeypatch.setattr(pyramid.threadlocal, "get_current_request", request)


def test_homepage_should_have_buzz_module_centerpage_should_not(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-magazin/index' % testserver.url)
    assert len(driver.find_elements_by_css_selector('.cp__buzz')) == 1
    driver.get('%s/centerpage/lebensart' % testserver.url)
    assert len(driver.find_elements_by_css_selector('.cp__buzz')) == 0

# commented out for first launch (as)
# def test_centerpage_should_have_pagetitle_in_body_but_hp_not(
#         selenium_driver, testserver):
#     driver = selenium_driver
#     driver.get('%s/zeit-magazin/index' % testserver.url)
#     assert len(driver.find_elements_by_css_selector('.cp__title')) == 0
#     driver.get('%s/centerpage/lebensart' % testserver.url)
#     pagetitle_in_body = driver.find_elements_by_css_selector('.cp__title')
#     assert pagetitle_in_body[0].text.strip() == "ZMO"


def test_centerpage_should_have_correct_page_title(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/lebensart' % testserver.url)
    title = driver.title.strip()
    assert title == u'ZEITmagazin ONLINE - Mode&Design, Essen&Trinken, Leben'


def test_centerpage_should_have_page_meta_description(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/lebensart' % testserver.url)
    meta_description_tag = driver.find_element_by_xpath(
        '//meta[@name="description"]')
    teststring = u'ZEITmagazin ONLINE - Mode&Design, Essen&Trinken, Leben'
    assert meta_description_tag.get_attribute("content").strip() == teststring


def test_centerpage_should_have_page_meta_keywords(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/lebensart' % testserver.url)
    meta_description_tag = driver.find_element_by_xpath(
        '//meta[@name="keywords"]')
    teststring = u'ZEIT ONLINE, ZEIT MAGAZIN'
    assert meta_description_tag.get_attribute("content").strip() == teststring


def test_most_sufficient_teaser_tpl_should_produce_correct_combinations():
    should = [
        'templates/inc/teaser/teaser_lead_article_video.html',
        'templates/inc/teaser/teaser_lead_article_default.html',
        'templates/inc/teaser/teaser_lead_default_video.html',
        'templates/inc/teaser/teaser_lead_default_default.html',
        'templates/inc/teaser/teaser_default_article_video.html',
        'templates/inc/teaser/teaser_default_article_default.html',
        'templates/inc/teaser/teaser_default_default_video.html',
        'templates/inc/teaser/teaser_default_default_default.html']
    result = most_sufficient_teaser_tpl('lead', 'article', 'video')
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


def test_cp_area_lead_has_expected_structure(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/lebensart' % testserver.url)
    wrap = driver.find_elements_by_css_selector(".main")
    assert len(wrap) != 0
    for element in wrap:
        main_lead_wrap = element.find_elements_by_css_selector(
            ".cp__lead__wrap")
        inf_lead_wrap = element.find_elements_by_css_selector(
            ".cp__lead__informatives__wrap")
        assert len(main_lead_wrap) != 0
        assert len(inf_lead_wrap) != 0


def test_cp_leadteaser_has_expected_structure(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/lebensart' % testserver.url)
    wrap = driver.find_elements_by_css_selector(".cp__lead-leader__wrap")
    assert len(wrap) != 0
    for element in wrap:
        text_wrap = element.find_elements_by_css_selector(
            ".cp__lead-leader__title__wrap--dark")
        link_wrap = element.find_elements_by_tag_name(
            "a")
        image_wrap = element.find_elements_by_css_selector(
            ".cp__lead-leader__image--dark")
        assert len(text_wrap) != 0
        assert len(link_wrap) == 3
        assert len(image_wrap) != 0


def test_cp_leadteaser_has_expected_text_content(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/lebensart' % testserver.url)
    wrap = driver.find_elements_by_css_selector(
        ".cp__lead-leader__title__wrap--dark")
    assert len(wrap) != 0
    for element in wrap:
        supertitle = element.find_element_by_css_selector(
            ".cp__lead__supertitle")
        title = element.find_element_by_css_selector(".cp__lead__title")
        subtitle = element.find_element_by_css_selector(".cp__lead__subtitle")
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
        ".cp__lead-leader__image--dark")
    assert len(wrap) != 0
    for element in wrap:
        img = element.find_element_by_tag_name(
            "img")
        assert re.search('http://.*/centerpage/katzencontent/' +
                         'bitblt-.*/' +
                         'katzencontent-zmo-square-large.jpg',
                         img.get_attribute("src"))
        print img.get_attribute("alt")
        print img.get_attribute("title")
        assert img.get_attribute("alt") == 'Die ist der Alttest'
        assert img.get_attribute("title") == 'Katze!'


def test_cp_leadteaser_has_expected_links(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/lebensart' % testserver.url)
    wrap = driver.find_elements_by_css_selector(".cp__lead-leader__wrap")
    assert len(wrap) != 0
    for element in wrap:
        link_wrap = element.find_elements_by_tag_name("a")
        assert len(link_wrap) == 3
        for link in link_wrap:
            assert link.get_attribute("href") == 'http://'\
                'localhost:6543/centerpage/article_image_asset'


def test_cp_img_button_has_expected_structure(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/lebensart' % testserver.url)
    wrap = driver.find_elements_by_css_selector(".cp__buttons__wrap")
    assert len(wrap) != 0
    for element in wrap:
        text_wrap = element.find_elements_by_css_selector(
            ".cp__buttons__title__wrap")
        link_wrap = element.find_elements_by_tag_name(
            "a")
        assert len(text_wrap) != 0
        assert len(link_wrap) >= 1


def test_cp_img_button_has_expected_img_content(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/lebensart' % testserver.url)
    wrap = driver.find_elements_by_css_selector(
        ".cp__buttons__image")
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
    driver.get('%s/centerpage/cp_with_image_lead' % testserver.url)
    wrap = driver.find_elements_by_css_selector(".cp__buttons__wrap")
    assert len(wrap) != 0
    for element in wrap:
        text_wrap = element.find_elements_by_css_selector(
            ".cp__buttons__title__wrap")
        link_wrap = element.find_elements_by_tag_name(
            "a")
        assert len(text_wrap) != 0
        assert len(link_wrap) == 1


def test_cp_button_has_expected_text_content(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/lebensart' % testserver.url)
    wrap = driver.find_elements_by_css_selector(
        ".cp__buttons__title__wrap")
    assert len(wrap) != 0
    for element in wrap:
        supertitle = element.find_element_by_css_selector(
            ".cp__buttons__supertitle")
        title = element.find_element_by_css_selector(".cp__buttons__title")
        subtitle = element.find_element_by_css_selector(
            ".cp__buttons__subtitle")
        assert unicode(supertitle.text) == u'Article Image Asset Spitzmarke'
        assert unicode(title.text) == u'Article Image Asset Titel'
        assert unicode(subtitle.text) == u'Dies k\u00F6nnte'\
            ' z.B. lorem ipsum sein.'\
            ' Oder was anderes nicht ganz so langweiliges,'\
            ' zum Katzenbild passen.'


def test_cp_button_has_expected_links(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/lebensart' % testserver.url)
    wrap = driver.find_elements_by_css_selector(".cp__buttons__wrap")
    assert len(wrap) != 0
    for element in wrap:
        link_wrap = element.find_elements_by_tag_name("a")
        print link_wrap
        assert len(link_wrap) != 0
        for link in link_wrap:
            assert link.get_attribute("href") == 'http://'\
                'localhost:6543/centerpage/article_image_asset'


def test_cp_large_button_has_expected_structure(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-magazin/test-cp/test-cp-zmo-2' % testserver.url)
    wrap = driver.find_elements_by_css_selector(".cp__buttons__large__wrap")
    assert len(wrap) != 0
    for element in wrap:
        text_wrap = element.find_elements_by_css_selector(
            ".cp__buttons__large__title__wrap")
        link_wrap = element.find_elements_by_tag_name(
            "a")
        assert len(text_wrap) != 0
        assert len(link_wrap) == 2


def test_cp_large_button_has_expected_text_content(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-magazin/test-cp/test-cp-zmo-2' % testserver.url)
    wrap = driver.find_elements_by_css_selector(
        ".cp__buttons__large__title__wrap")
    assert len(wrap) != 0
    for element in wrap:
        supertitle = element.find_element_by_css_selector(
            ".cp__buttons__supertitle")
        title = element.find_element_by_css_selector(
            ".cp__buttons__large__title")
        assert unicode(supertitle.text) == u'Serie Gesellschaftskritik'
        assert unicode(title.text) == u'\u00DCBER SCHLECHTE LAUNE'


def test_cp_large_button_has_expected_links(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-magazin/test-cp/test-cp-zmo-2' % testserver.url)
    wrap = driver.find_elements_by_css_selector(".cp__buttons__large__wrap")
    assert len(wrap) != 0
    for element in wrap:
        link_wrap = element.find_elements_by_tag_name("a")
        print link_wrap
        assert len(link_wrap) != 0
        for link in link_wrap:
            assert re.search(
                'http://.*/zeit-magazin/test-cp/' +
                'gesellschaftskritik-grumpy-cat',
                link.get_attribute("href"))


def test_cp_should_have_informatives_ad_at_3rd_place(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-magazin/test-cp/test-cp-zmo' % testserver.url)
    wrap = driver.find_elements_by_css_selector(
        ".cp__lead__informatives__wrap")
    assert len(wrap) != 0
    elements = wrap[0].find_elements_by_tag_name("div")
    add = elements[2].get_attribute("class")
    assert add == 'cp__buttons__ad'
    mr = elements[2].find_element_by_css_selector(
        "#iqadtile7").get_attribute("class")
    assert mr == "ad__tile_7 ad__on__centerpage ad__width_300 ad__min__768"


def test_cp_with_video_lead_has_correct_markup(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/cp_with_video_lead' % testserver.url)
    wrap = driver.find_elements_by_css_selector(".cp__lead-full__wrap")
    assert len(wrap) != 0
    for teaser in wrap:
        vid_wrap = teaser.find_element_by_class_name("cp__lead-full--dark")
        vid = teaser.find_element_by_tag_name("video")
        img = teaser.find_element_by_tag_name("img")
        title_wrap = teaser.find_element_by_tag_name("header")
        h1 = teaser.find_element_by_tag_name("h1")
        a = teaser.find_elements_by_tag_name("a")
        subtitle = teaser.find_element_by_tag_name("span")
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
        assert 'video--fallback' == unicode(img.get_attribute("class"))
        assert 'cp__lead-full__title__wrap cp__lead-full__title__wrap--dark' == \
            unicode(title_wrap.get_attribute("class"))
        assert 'cp__lead__title' == unicode(h1.get_attribute("class"))
        assert 'cp__lead__subtitle' == unicode(subtitle.get_attribute("class"))

        # content
        assert '3035864892001' == \
            unicode(vid_wrap.get_attribute("data-backgroundvideo"))
        assert 'Es leben die Skispringenden Sportredakteure!' == \
            unicode(subtitle.text)
        assert src_img == unicode(img.get_attribute("src"))
        assert u'und der Titel dazu' == unicode(h1.text)
        assert src1_val == unicode(source1)
        assert src2_val == unicode(source2)

        # links
        assert len(a) == 3
        for link in a:
            assert link.get_attribute("href") == 'http://localhost'\
                ':6543/centerpage/article_video_asset'


def test_cp_with_image_lead_has_correct_markup(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/cp_with_image_lead' % testserver.url)
    wrap = driver.find_elements_by_css_selector(".cp__lead-full__wrap")
    assert len(wrap) != 0
    for teaser in wrap:
        img_wrap = teaser.find_elements_by_class_name("cp__lead-full--dark")
        img = teaser.find_element_by_tag_name("img")
        title_wrap = teaser.find_elements_by_tag_name("header")
        h1 = teaser.find_element_by_tag_name("h1")
        a = teaser.find_elements_by_tag_name("a")
        subtitle = teaser.find_element_by_tag_name("span")
        image_pattern = \
            'http://.*/centerpage/katzencontent/'\
            'bitblt-.*'\
            '/katzencontent-zmo-landscape-large.jpg'

        # structure
        assert len(img_wrap) != 0
        assert len(title_wrap) != 0

        assert re.search(image_pattern, img.get_attribute("src"))
        assert unicode(h1.text) == u'Article Image Asset Titel'
        assert unicode(subtitle.text) == u'Dies k\u00F6nnte'\
            ' z.B. lorem ipsum sein.'\
            ' Oder was anderes nicht ganz so langweiliges,'\
            ' zum Katzenbild passen.'
        assert img.get_attribute("alt") == 'Die ist der Alttest'
        assert img.get_attribute("title") == 'Katze!'

        # links
        assert len(a) == 3
        for link in a:
            assert link.get_attribute("href") == 'http://localhost'\
                ':6543/centerpage/article_image_asset'


def test_teaser_light_versions_are_working(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-magazin/test-cp/test-cp-zmo-2' % testserver.url)
    teaser = driver.find_elements_by_css_selector(".cp__lead-full--light")
    assert len(teaser) != 0

    driver.get('%s/centerpage/lebensart-2' % testserver.url)
    teaser = driver.find_elements_by_css_selector(
        ".cp__lead-leader__image--light")
    assert len(teaser) != 0


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
    teaser_img = most_sufficient_teaser_image(teaser_block, article_context)
    assert zeit.frontend.interfaces.ITeaserImage.providedBy(teaser_img)


def test_teaser_image_url_should_be_created(
        testserver, monkeyreq):
    cp = 'http://xml.zeit.de/centerpage/lebensart'
    cp_context = zeit.cms.interfaces.ICMSContent(cp)
    teaser_block = cp_context['lead'][0]

    article = 'http://xml.zeit.de/centerpage/article_image_asset'
    article_context = zeit.cms.interfaces.ICMSContent(article)

    teaser_image = most_sufficient_teaser_image(teaser_block, article_context)

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
    request.registry.settings.node_comment_statistics = app_settings['node_comment_statistics']

    cp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo')
    view = zeit.frontend.view_centerpage.Centerpage(cp, request)

    buzz = view.area_buzz
    assert set(buzz.keys()) == {'facebook', 'twitter', 'comments'}
    assert len(buzz['facebook']) == 3
    assert len(buzz['twitter']) == 3
    assert len(buzz['comments']) == 3


def test_centerpages_produces_no_error(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-magazin/test-cp/test-cp-zmo' % testserver.url)
    assert len(driver.find_elements_by_css_selector('.page-wrap')) != 0
    driver.get('%s/zeit-magazin/test-cp/test-cp-zmo-2' % testserver.url)
    assert len(driver.find_elements_by_css_selector('.page-wrap')) != 0
    driver.get('%s/centerpage/cp_with_image_lead' % testserver.url)
    assert len(driver.find_elements_by_css_selector('.page-wrap')) != 0
    driver.get('%s/centerpage/cp_with_video_lead' % testserver.url)
    assert len(driver.find_elements_by_css_selector('.page-wrap')) != 0
    driver.get('%s/centerpage/lebensart-2' % testserver.url)
    assert len(driver.find_elements_by_css_selector('.page-wrap')) != 0
    driver.get('%s/centerpage/lebensart' % testserver.url)
    assert len(driver.find_elements_by_css_selector('.page-wrap')) != 0


def test_cp_lead_should_have_correct_first_block(application):
    cp = 'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo-2'
    cp_context = zeit.cms.interfaces.ICMSContent(cp)
    cp_view = view_centerpage.Centerpage(cp_context, mock.Mock())
    lead1_first_block = 'http://block.vivi.zeit.de/http://xml.zeit.de/'\
        'zeit-magazin/test-cp/test-cp-zmo-2#'\
        'lead/id-f8f46488-75ea-46f4-aaff-7654b4e1c805'
    lead1_last_block = 'http://block.vivi.zeit.de/http://xml.zeit.de/'\
        'zeit-magazin/test-cp/test-cp-zmo-2#lead/'\
        'id-eae7c703-98e9-491a-a30d-c1c5cebd2371'
    assert lead1_first_block == cp_view.area_lead1[0].uniqueId
    assert lead1_last_block == cp_view.area_lead1[3].uniqueId


def test_cp_lead_should_have_correct_second_block(application):
    cp = 'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo-2'
    cp_context = zeit.cms.interfaces.ICMSContent(cp)
    cp_view = view_centerpage.Centerpage(cp_context, mock.Mock())
    lead2_first_block = 'http://block.vivi.zeit.de/http://xml.zeit.de/'\
        'zeit-magazin/test-cp/test-cp-zmo-2#lead/'\
        'id-cc6bbea3-1337-42f5-8fe1-01c9c4476600'
    lead2_last_block = 'http://block.vivi.zeit.de/http://xml.zeit.de/'\
        'zeit-magazin/test-cp/test-cp-zmo-2#lead/'\
        'id-f8f46488-75ea-46f4-aaff-7654b4e1c805'
    assert lead2_first_block == cp_view.area_lead2[0].uniqueId
    assert lead2_last_block == cp_view.area_lead2[1].uniqueId


def test_cp_lead_should_have_no_blocks(application):
    cp = 'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo'
    cp_context = zeit.cms.interfaces.ICMSContent(cp)
    cp_view = view_centerpage.Centerpage(cp_context, mock.Mock())
    lead_first_block = 'http://block.vivi.zeit.de/http://xml.zeit.de/'\
        'zeit-magazin/test-cp/test-cp-zmo#lead/'\
        'id-f8f46488-75ea-46f4-aaff-7654b4e1c805'
    lead_last_block = 'http://block.vivi.zeit.de/http://xml.zeit.de/'\
        'zeit-magazin/test-cp/test-cp-zmo#lead/'\
        'id-48962e5e-cdbe-4148-a12c-17724cd0e96b'
    assert lead_first_block == cp_view.area_lead1[0].uniqueId
    assert lead_last_block == cp_view.area_lead1[3].uniqueId


def test_cp_informatives_should_have_correct_first_block(application):
    cp = 'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo-2'
    cp_context = zeit.cms.interfaces.ICMSContent(cp)
    cp_view = view_centerpage.Centerpage(cp_context, mock.Mock())
    informatives1_first_block = 'http://block.vivi.zeit.de/'\
        'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo-2'\
        '#informatives/id-3d2116f6-96dd-4556-81f7-d7d0a40435e5'
    informatives1_last_block = 'http://block.vivi.zeit.de/'\
        'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo-2'\
        '#informatives/id-bff224c9-088e-40d4-987d-9d986de804bd'

    assert informatives1_first_block == cp_view.area_informatives1[0].uniqueId
    assert informatives1_last_block == cp_view.area_informatives1[1].uniqueId


def test_cp_informatives_should_have_correct_second_block(application):
    cp = 'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo-2'
    cp_context = zeit.cms.interfaces.ICMSContent(cp)
    cp_view = view_centerpage.Centerpage(cp_context, mock.Mock())
    informatives2_first_block = 'http://block.vivi.zeit.de/'\
        'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo-2'\
        '#informatives/id-edc55a53-7cab-4bbc-a31d-1cf20afe5d9d'
    informatives2_last_block = 'http://block.vivi.zeit.de/'\
        'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo-2'\
        '#informatives/id-3d2116f6-96dd-4556-81f7-d7d0a40435e5'

    assert informatives2_first_block == cp_view.area_informatives2[0].uniqueId
    assert informatives2_last_block == cp_view.area_informatives2[1].uniqueId


def test_cp_informatives_should_have_no_blocks(application):
    cp = 'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo'
    cp_context = zeit.cms.interfaces.ICMSContent(cp)
    cp_view = view_centerpage.Centerpage(cp_context, mock.Mock())
    informatives_first_block = 'http://block.vivi.zeit.de/'\
        'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo'\
        '#informatives/id-3d2116f6-96dd-4556-81f7-d7d0a40435e5'
    informatives_last_block = 'http://block.vivi.zeit.de/'\
        'http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo'\
        '#informatives/id-edc55a53-7cab-4bbc-a31d-1cf20afe5d9d'

    assert informatives_first_block == cp_view.area_informatives1[0].uniqueId
    assert informatives_last_block == cp_view.area_informatives1[2].uniqueId


def test_cp_teaser_should_have_comment_count(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-magazin/test-cp/test-cp-zmo-2' % testserver.url)
    wrap = driver.find_elements_by_css_selector(".cp__comment__count__wrap")
    comments = wrap[0].text
    assert len(wrap) != 0
    assert comments == '22'


def test_centerpage_should_have_monothematic_block(application):
    cp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/zeit-magazin/test-cp/test-cp-zmo')
    view = zeit.frontend.view_centerpage.Centerpage(cp, mock.Mock())
    assert len(view.monothematic_block) == 6


def test_centerpage_should_have_no_monothematic_block(application):
    cp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/centerpage/lebensart')
    view = zeit.frontend.view_centerpage.Centerpage(cp, mock.Mock())
    assert view.monothematic_block is None
