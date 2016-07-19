# -*- coding: utf-8 -*-
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC  # NOQA
from selenium.webdriver.support.ui import WebDriverWait
import pytest
import requests

import zeit.cms.interfaces
import zeit.content.image.interfaces
import zeit.content.video.video

import zeit.web.core.application
import zeit.web.core.template
import zeit.web.site.module.playlist
import zeit.web.site.view_video


def test_video_imagegroup_should_adapt_videos(application):
    video = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/video/3537342483001')
    group = zeit.content.image.interfaces.IImageGroup(video)
    assert isinstance(group, zeit.web.site.module.playlist.ImageGroup)


@pytest.mark.parametrize('img,size,res', [
    ('wide', 276518, (580, 326)),
    ('cinema', 217003, (580, 248))
])
def test_video_imagegroup_should_set_local_image_fileobj(
        img, size, res, application):
    unique_id = 'http://xml.zeit.de/zeit-online/video/3537342483001'
    video = zeit.cms.interfaces.ICMSContent(unique_id)
    group = zeit.content.image.interfaces.IImageGroup(video)
    image = group[img]
    assert image.size == size
    assert image.getImageSize() == res


def test_video_page_should_feature_sharing_images(testbrowser):
    doc = testbrowser('/zeit-online/video/3537342483001').document
    assert doc.xpath('//meta[@property="og:image"]/@content')[0].endswith(
        '/zeit-online/video/3537342483001/imagegroup/wide__1300x731')
    assert doc.xpath('//meta[@name="twitter:image"]/@content')[0].endswith(
        '/zeit-online/video/3537342483001/imagegroup/wide__1300x731')


def test_video_page_should_feature_schema_org_props(testbrowser):
    doc = testbrowser('/zeit-online/video/3537342483001').document
    assert doc.xpath('//meta[@itemprop="duration" and @content="PT436S"]')
    assert doc.xpath('//meta[@itemprop="thumbnailUrl"]/@content')[0].endswith(
        '/zeit-online/video/3537342483001/imagegroup/wide')
    assert doc.xpath('//meta[@itemprop="duration" and @content="PT436S"]')
    assert doc.xpath(
        '//meta[@itemprop="playerType" and @content="HTML5 Flash"]')
    assert doc.xpath(
        u'//meta[@itemprop="name" and ' +
        u'@content="Roboter Myon übernimmt Opernrolle"]')
    assert doc.xpath(
        u'//meta[@itemprop="uploadDate" and ' +
        u'@content="2015-01-22T10:27:01+01:00"]')


def test_video_page_should_print_out_video_headline(testbrowser):
    browser = testbrowser('/zeit-online/video/3537342483001')
    headline = browser.xpath('//h1[@itemprop="headline"]/span/text()')
    assert headline[0].strip() == u'Künstliche Intelligenz'
    assert headline[1] == u': '
    assert headline[2].strip() == u'Roboter Myon übernimmt Opernrolle'


def test_video_page_should_render_video_description(testbrowser):
    doc = testbrowser('/zeit-online/video/3537342483001').document
    assert u'Er ist so groß wie ein siebenjähriges Kind und lernt noch' in (
        doc.xpath('//div[@itemprop="description"]/text()')[0])


def test_video_page_should_display_modified_date(testbrowser):
    doc = testbrowser('/zeit-online/video/3537342483001').document
    assert '22. Januar 2015, 10:27' in doc.xpath(
        '//time[@datetime]/text()')[0]


@pytest.mark.xfail(reason='Comment module is to be included on video pages.')
def test_video_page_should_output_zero_comment_count(testbrowser):
    doc = testbrowser('/zeit-online/video/3537342483001').document
    assert 'Noch keine Kommentare.' in doc.xpath(
        '//span[@itemprop="commentCount"]/text()')[0]
    assert doc.xpath('//meta[@itemprop="commentCount" and @content="0"]')


@pytest.mark.xfail(reason='Comment module is to be included on video pages.')
def test_video_page_should_output_comment_count_number(
        testserver, testbrowser, monkeypatch):
    attr = {'comment_count': 7, 'pages': {'title', 'meh'}, 'headline': 'bar'}
    monkeypatch.setattr(zeit.web.site.view_video.Video, 'comments', attr)
    doc = testbrowser('/zeit-online/video/3537342483001').document
    assert 'bar' in doc.xpath('//span[@itemprop="commentCount"]/text()')[0]


def test_video_comment_thread_should_be_rendered(testbrowser):
    browser = testbrowser('/zeit-online/video/3537342483001/comment-thread')
    assert len(browser.cssselect('.comment-section__head')) == 1


def test_video_comment_form_should_be_rendered(testbrowser):
    browser = testbrowser('/zeit-online/video/3537342483001/comment-form')
    assert len(browser.cssselect('#comment-form')) == 1


def test_video_report_form_should_be_rendered(testbrowser):
    browser = testbrowser('/zeit-online/video/3537342483001/report-form')
    assert len(browser.cssselect('#comment-form')) == 1


def test_video_page_should_embed_sharing_menu(testbrowser):
    browser = testbrowser('/zeit-online/video/3537342483001')
    assert len(browser.cssselect('.sharing-menu .sharing-menu__title')) > 0
    assert len(browser.cssselect('.sharing-menu a.sharing-menu__link')) > 0


def test_video_page_video_iframe_should_exist(testserver, testbrowser):
    browser = testbrowser('/zeit-online/video/3537342483001')
    assert len(browser.cssselect('.video-player__iframe')) > 0


def test_video_page_video_should_exist(selenium_driver, testserver):

    driver = selenium_driver
    driver.get('{}/zeit-online/video/3537342483001'.format(testserver.url))

    iframe = driver.find_element_by_css_selector(
        '.video-player__iframe')
    driver.switch_to.frame(iframe)

    try:
        player = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '.video-js')))
        assert player
    except TimeoutException:
        assert False, 'Video not visible within 20 seconds'


def test_video_page_adcontroller_code_is_embedded(testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'third_party_modules': True}.get)

    browser = testbrowser('/zeit-online/video/3537342483001')
    assert len(browser.cssselect('#ad-desktop-7')) == 1


def test_create_url_filter_should_append_seo_slug_to_all_video_links(
        application, dummy_request):
    video = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/video/3537342483001')
    assert zeit.web.core.template.create_url(None, video, dummy_request) == (
        'http://example.com/zeit-online/video/3537342483001'
        '/kuenstliche-intelligenz-roboter-myon-uebernimmt-opernrolle')


def test_create_url_filter_should_handle_empty_supertitles(application):
    video = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/video/2014-01/1953013471001')
    assert zeit.web.core.template.create_url(None, video) == (
        '/video/2014-01/1953013471001/foto-momente'
        '-die-stille-schoenheit-der-polarlichter')


def test_video_page_should_redirect_to_slug_from_plain_id_url(
        testserver, testbrowser):
    path = '/zeit-online/video/3537342483001'
    slug = '/kuenstliche-intelligenz-roboter-myon-uebernimmt-opernrolle'

    resp = requests.get(testserver.url + path, allow_redirects=False)
    assert resp.headers.get('Location', '') == testserver.url + path + slug

    resp = requests.get(testserver.url + path, allow_redirects=True)
    assert resp.url == testserver.url + path + slug


def test_video_page_should_redirect_to_correct_slug_from_faulty_slug(
        testserver, testbrowser):
    path = '/zeit-online/video/3537342483001'
    slug = '/kuenstliche-intelligenz-roboter-myon-uebernimmt-opernrolle'

    resp = requests.get(testserver.url + path + '/foo', allow_redirects=False)
    assert resp.headers.get('Location', '') == testserver.url + path + slug

    resp = requests.get(testserver.url + path + '/foo', allow_redirects=True)
    assert resp.url == testserver.url + path + slug


def test_video_page_should_not_redirect_from_correct_slug_url(
        testserver, testbrowser):
    path = '/zeit-online/video/3537342483001'
    slug = '/kuenstliche-intelligenz-roboter-myon-uebernimmt-opernrolle'

    resp = requests.get(testserver.url + path + slug, allow_redirects=False)
    assert 'Location' not in resp.headers

    resp = requests.get(testserver.url + path + slug, allow_redirects=True)
    assert resp.url == testserver.url + path + slug


def test_video_teaser_should_be_identified_as_such(application):
    video = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/video/2014-01/1953013471001')
    assert zeit.web.core.template.is_video(video)


def test_article_teaser_should_not_be_identified_as_video(application):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/image/crystal-meth-nancy-schmidt')
    assert not zeit.web.core.template.is_video(article)


def test_video_should_contain_veeseo_widget(testbrowser):
    select = testbrowser('/zeit-online/video/3537342483001').cssselect
    assert select('script[src="http://rce.veeseo.com/widgets/zeit/widget.js"]')
    assert select('.RV2VW2')


def test_video_should_not_break_on_missing_still_image(
        testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.content.video.video.Video, 'video_still', None)
    testbrowser('/zeit-online/video/3537342483001')


def test_expired_video_should_trigger_redirect(testserver):
    resp = requests.get(
        '%s/zeit-online/video/3537342483002' % testserver.url,
        allow_redirects=False)
    assert resp.status_code == 301
    assert (resp.headers['location'] == (
            '%s/video/index' % testserver.url))


def test_video_has_default_product_id(application, dummy_request):
    video = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/video/3537342483001')
    view = zeit.web.site.view_video.Video(video, dummy_request)
    assert view.product_id == 'zede'


def test_video_page_has_proper_article_tags(testbrowser):
    browser = testbrowser('/zeit-online/video/3537342483001')
    taglist = browser.cssselect('.article-tags')
    taglinks = browser.cssselect('.article-tags li a')
    assert len(taglist) > 0
    for taglink in taglinks:
        assert taglink.get('class').endswith('--video')
