from pytest import fixture
from zeit.frontend.application import default_image_url
from zeit.frontend.application import most_sufficient_teaser_img
from zeit.frontend.application import most_sufficient_teaser_tpl
import mock
import pyramid.threadlocal
import re
import zeit.cms.interfaces
import zeit.content.gallery.gallery
import zeit.frontend.interfaces
import zeit.frontend.view_centerpage


@fixture
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
    assert title == 'Lebensart - Mode, Essen und Trinken, Partnerschaft | ZEIT ONLINE'


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


def test_cp_area_lead_should_have_expected_markup(jinja2_env, testserver):
    tpl = jinja2_env.get_template('templates/inc/cp_area_lead.html')
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/centerpage/lebensart')

    # We need a view
    view = zeit.frontend.view_centerpage.Centerpage(cp, '')
    result = [u"<div class='area__lead'>",
              u"            <div class='teaser_block__default'>",
              u"            <div class='teaser__default'>",
              u"        <h2 title='Gentrifizierung \u2013 Mei, is des traurig!'>",
              u"        <a href=''>",
              u"            <span class='teaser__supertitle teaser__default__supertitle'>Gentrifizierung</span>",
              u"            <span class='teaser__title teaser__default__title'>Mei, is des traurig!</span>",
              u'        </a>',
              u'    </h2>',
              ]
    render = tpl.render(view=view, request=view.request).splitlines()
    assert render[:9] == result



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
        assert 'und der Titel dazu' == unicode(h1.text)
        assert src1_val == unicode(source1)
        assert src2_val == unicode(source2)


def test_default_image_url_should_return_default_image_size(
        testserver, monkeyreq):
    image_id = \
        'http://xml.zeit.de/centerpage/katzencontent/katzencontent-180x101.jpg'
    image = zeit.cms.interfaces.ICMSContent(image_id)
    image_url = default_image_url(image)
    assert re.search(
        'http://example.com/centerpage/katzencontent/bitblt-200x300-.*/katzencontent-180x101.jpg',
        image_url)


def test_default_image_url_should_return_available_image_size(
        testserver, monkeyreq):
    image_id = \
        'http://xml.zeit.de/centerpage/katzencontent/katzencontent-180x101.jpg'
    image = zeit.cms.interfaces.ICMSContent(image_id)
    image_url = default_image_url(image)
    assert re.search(
        'http://example.com/centerpage/katzencontent/bitblt-200x300-.*/katzencontent-180x101.jpg',
        image_url)


def test_default_image_url_should_return_None_when_no_uniqueId_is_given(
        testserver, monkeyreq):
    m = mock.Mock()
    assert default_image_url(m) is None


def test_default_teaser_should_return_default_teaser_image(
        testserver, monkeyreq):
    article = 'http://xml.zeit.de/centerpage/article_image_asset'
    article_context = zeit.cms.interfaces.ICMSContent(article)

    cp = 'http://xml.zeit.de/centerpage/lebensart'
    cp_context = zeit.cms.interfaces.ICMSContent(cp)
    teaser_block = cp_context['lead'][0]

    teaser_img = most_sufficient_teaser_img(teaser_block, article_context)
    assert re.search(
        "http://example.com/centerpage/katzencontent/bitblt-200x300.*katzencontent-540x304.jpg",
        teaser_img)

