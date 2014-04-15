from zeit.frontend import view_centerpage
from zope.component import getMultiAdapter
from zeit.frontend.application import default_image_url
from zeit.frontend.application import most_sufficient_teaser_image
from zeit.frontend.application import most_sufficient_teaser_tpl
from zeit.frontend.application import create_image_url
from zeit.frontend.application import get_image_metadata
import mock
import pyramid.threadlocal
import pytest
import re
import zeit.cms.interfaces
import zeit.content.gallery.gallery
import zeit.frontend.interfaces
import zeit.frontend.view_centerpage


@pytest.fixture
def monkeyreq(monkeypatch):
    def request():
        m = mock.Mock()
        m.route_url = lambda x: "http://example.com/"
        return m

    monkeypatch.setattr(pyramid.threadlocal, "get_current_request", request)


def test_centerpage_should_have_correct_page_title(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/lebensart' % testserver.url)
    title = driver.title.strip()
    assert title == 'Lebensart - Mode, Essen und Trinken' \
                    ', Partnerschaft | ZEIT ONLINE'


def test_centerpage_should_have_page_meta_description(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/lebensart' % testserver.url)
    meta_description_tag = driver.find_element_by_xpath(
        '//meta[@name="description"]')
    teststring = 'Die Lust am Leben: Aktuelle Berichte, Ratgeber und...'
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
    assert type(asset) == zeit.content.gallery.gallery.Gallery


def test_autoselected_asset_from_cp_teaser_should_be_an_image(testserver):
    article = 'http://xml.zeit.de/centerpage/article_image_asset'
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.frontend.centerpage.auto_select_asset(context)
    assert type(asset) == zeit.content.image.imagegroup.ImageGroup


def test_autoselected_asset_from_cp_teaser_should_be_a_video(testserver):
    article = 'http://xml.zeit.de/centerpage/article_video_asset'
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.frontend.centerpage.auto_select_asset(context)
    assert type(asset) == zeit.content.video.video.Video


def test_autoselected_asset_from_cp_teaser_should_be_a_video_list(testserver):
    article = 'http://xml.zeit.de/centerpage/article_video_asset_2'
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.frontend.centerpage.auto_select_asset(context)
    assert type(asset[0]) == zeit.content.video.video.Video
    assert type(asset[1]) == zeit.content.video.video.Video


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
            ".cp__lead-leader__title__wrap")
        link_wrap = element.find_elements_by_tag_name(
            "a")
        image_wrap = element.find_elements_by_css_selector(
            ".cp__lead-leader__image")
        assert len(text_wrap) != 0
        assert len(link_wrap) == 3
        assert len(image_wrap) != 0


def test_cp_leadteaser_has_expected_text_content(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/lebensart' % testserver.url)
    wrap = driver.find_elements_by_css_selector(
        ".cp__lead-leader__title__wrap")
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
        ".cp__lead-leader__image")
    assert len(wrap) != 0
    for element in wrap:
        img = element.find_element_by_tag_name(
            "img")
        assert img.get_attribute("src") == 'http://'\
            '127.0.0.1:6543/centerpage/katzencontent/'\
            'bitblt-200x300-c302245709334b3eb72a8de061de81a6d193e3d5/'\
            'katzencontent-540x304.jpg'
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
                '127.0.0.1:6543/centerpage/article_image_asset'


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
        image_wrap = element.find_elements_by_css_selector(
            ".cp__buttons__image")
        assert len(text_wrap) != 0
        assert len(link_wrap) == 3
        assert len(image_wrap) != 0


def test_cp_img_button_has_expected_img_content(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/lebensart' % testserver.url)
    wrap = driver.find_elements_by_css_selector(
        ".cp__buttons__image")
    assert len(wrap) != 0
    for element in wrap:
        img = element.find_element_by_tag_name(
            "img")
        assert img.get_attribute("src") == 'http://'\
            '127.0.0.1:6543/centerpage/katzencontent/'\
            'bitblt-640x480-9233bf866124e837824b56b39c8df60148115b15/'\
            'katzencontent-148x84.jpg'
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
        assert len(link_wrap) == 2


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
        assert len(link_wrap) == 3
        for link in link_wrap:
            assert link.get_attribute("href") == 'http://'\
                '127.0.0.1:6543/centerpage/article_image_asset'


def test_cp_with_video_lead_has_correct_markup(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/cp_with_video_lead' % testserver.url)
    wrap = driver.find_elements_by_css_selector(".cp__lead-full__wrap")
    assert len(wrap) != 0
    for teaser in wrap:
        vid_wrap = teaser.find_element_by_class_name("cp__lead-full")
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
            'http://brightcove.vo.llnwd.net/pd15/media/18140073001/201401/' \
            '927/18140073001_3035897844001_Beitrag-' \
            'Skispringen-f-r-Anf-nger.mp4'
        src2_val = \
            'http://opendata.zeit.de/zmo-videos/3035864892001.webm'
        src_img = \
            'http://brightcove.vo.llnwd.net/d21/unsecured/media/' \
            '18140073001/201401/2713/18140073001_3035871869001' \
            '_Skispringen.jpg?pubId=18140073001'

        #structure
        assert 'true' == unicode(vid.get_attribute("autoplay"))
        assert 'video--fallback' == unicode(img.get_attribute("class"))
        assert 'cp__lead-full__title__wrap' == \
            unicode(title_wrap.get_attribute("class"))
        assert 'cp__lead__title' == unicode(h1.get_attribute("class"))
        assert 'cp__lead__subtitle' == unicode(subtitle.get_attribute("class"))

        #content
        assert '3035864892001' == \
            unicode(vid_wrap.get_attribute("data-backgroundvideo"))
        assert 'Es leben die Skispringenden Sportredakteure!' == \
            unicode(subtitle.text)
        assert src_img == unicode(img.get_attribute("src"))
        assert u'\u00ABund der Titel dazu\u00BB' == unicode(h1.text)
        assert src1_val == unicode(source1)
        assert src2_val == unicode(source2)

        #links
        assert len(a) == 3
        for link in a:
            assert link.get_attribute("href") == 'http://127.0.0.1'\
                ':6543/centerpage/article_video_asset'


def test_cp_with_image_lead_has_correct_markup(selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/centerpage/cp_with_image_lead' % testserver.url)
    wrap = driver.find_elements_by_css_selector(".cp__lead-full__wrap")
    assert len(wrap) != 0
    for teaser in wrap:
        img_wrap = teaser.find_elements_by_class_name("cp__lead-full")
        img = teaser.find_element_by_tag_name("img")
        title_wrap = teaser.find_elements_by_tag_name("header")
        h1 = teaser.find_element_by_tag_name("h1")
        a = teaser.find_elements_by_tag_name("a")
        subtitle = teaser.find_element_by_tag_name("span")
        src_img = \
            'http://127.0.0.1:6543/centerpage/katzencontent/'\
            'bitblt-640x480-9233bf866124e837824b56b39c8df601'\
            '48115b15/katzencontent-940x400.jpg'

        #structure
        assert len(img_wrap) != 0
        assert len(title_wrap) != 0

        #content
        assert src_img == unicode(img.get_attribute("src"))
        assert unicode(h1.text) == u'\u00ABArticle Image Asset Titel\u00BB'
        assert unicode(subtitle.text) == u'Dies k\u00F6nnte'\
            ' z.B. lorem ipsum sein.'\
            ' Oder was anderes nicht ganz so langweiliges,'\
            ' zum Katzenbild passen.'
        assert img.get_attribute("alt") == 'Die ist der Alttest'
        assert img.get_attribute("title") == 'Katze!'

        #links
        assert len(a) == 3
        for link in a:
            assert link.get_attribute("href") == 'http://127.0.0.1'\
                ':6543/centerpage/article_image_asset'


def test_get_image_asset_should_return_image_asset(testserver):
    article = 'http://xml.zeit.de/centerpage/article_image_asset'
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.frontend.centerpage.get_image_asset(
        context)
    assert type(asset) == zeit.content.image.imagegroup.ImageGroup


def test_get_gallery_asset_should_return_gallery_asset(testserver):
    article = 'http://xml.zeit.de/centerpage/article_gallery_asset'
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.frontend.centerpage.get_gallery_asset(
        context)
    assert type(asset) == zeit.content.gallery.gallery.Gallery


def test_get_video_asset_should_return_video_asset(testserver):
    article = 'http://xml.zeit.de/centerpage/article_video_asset'
    context = zeit.cms.interfaces.ICMSContent(article)
    asset = zeit.frontend.centerpage.get_video_asset(
        context)
    assert type(asset) == zeit.content.video.video.Video


def test_default_image_url_should_return_default_image_size(
        testserver, monkeyreq):
    image_id = \
        'http://xml.zeit.de/centerpage/katzencontent/katzencontent-180x101.jpg'
    image = zeit.cms.interfaces.ICMSContent(image_id)
    image_url = default_image_url(image)
    assert re.search(
        'http://example.com/centerpage/katzencontent/'
        'bitblt-200x300-.*/katzencontent-180x101.jpg',
        image_url)


def test_default_image_url_should_return_available_image_size(
        testserver, monkeyreq):
    image_id = \
        'http://xml.zeit.de/centerpage/katzencontent/katzencontent-180x101.jpg'
    image = zeit.cms.interfaces.ICMSContent(image_id)
    image_url = default_image_url(image)
    assert re.search(
        'http://example.com/centerpage/katzencontent/'
        'bitblt-200x300-.*/katzencontent-180x101.jpg',
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
    assert zeit.content.image.interfaces.IImage.providedBy(teaser_img)


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
        "bitblt-200x300.*katzencontent-540x304.jpg",
        image_url)


def test_teaser_image_should_be_created_from_image_group_and_image(testserver):
    import zeit.cms.interfaces
    img = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/centerpage/'\
        'katzencontent/katzencontent-148x84.jpg')
    imgrp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/centerpage/'\
        'katzencontent/')
    teaser_image = getMultiAdapter(
        (imgrp,img),
        zeit.frontend.centerpage.ITeaserImage)

    assert teaser_image.caption == 'Die ist der image sub text'
    assert teaser_image.src == img.uniqueId
    assert teaser_image.attr_alt == 'Die ist der Alttest'
    assert teaser_image.attr_title == 'Katze!'


def test_image_metadata_should_be_accessible(testserver):
    cp = 'http://xml.zeit.de/centerpage/lebensart'
    cp_context = zeit.cms.interfaces.ICMSContent(cp)
    teaser_block = cp_context['lead'][0]

    article = 'http://xml.zeit.de/centerpage/article_image_asset'
    article_context = zeit.cms.interfaces.ICMSContent(article)

    teaser_img = most_sufficient_teaser_image(teaser_block, article_context)
    img_meta = get_image_metadata(teaser_img)
    assert zeit.content.image.interfaces.IImageMetadata.providedBy(img_meta)
    assert img_meta.title == u'Katze!'
    assert img_meta.alt == u'Die ist der Alttest'
    assert img_meta.caption == u'Die ist der image sub text'


def test_get_reaches_from_centerpage_view(dummy_request):
    view = view_centerpage.Centerpage('', dummy_request)
    assert len(view.global_twitter_shares) == 10
    assert len(view.global_googleplus_shares) == 10
    assert len(view.global_facebook_shares) == 10
