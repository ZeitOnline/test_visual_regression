# -*- coding: utf-8 -*-
import re

import pytest
import requests

import zeit.cms.interfaces
import zeit.content.image.interfaces

import zeit.web.core.centerpage
import zeit.web.site.view_video

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC  # NOQA
from selenium.webdriver.support.ui import WebDriverWait


def is_adcontrolled(contents):
    return 'data-adDeliveryType="adcontroller"' in contents


# use this to enable third_party_modules
def tpm(me):
    return True


def test_video_imagegroup_should_adapt_videos(application):
    video = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/video/2015-01/3537342483001')
    group = zeit.content.image.interfaces.IImageGroup(video)
    assert isinstance(group, zeit.web.core.centerpage.VideoImageGroup)


def test_video_imagegroup_should_contain_two_images(application):
    video = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/video/2015-01/3537342483001')
    group = zeit.content.image.interfaces.IImageGroup(video)
    assert set(group.keys()) == {'still.jpg', 'thumbnail.jpg'}


@pytest.mark.parametrize('img', ['still', 'thumbnail'])
def test_video_imagegroup_should_set_appropriate_properties(img, application):
    unique_id = 'http://xml.zeit.de/video/2015-01/3537342483001'
    video = zeit.cms.interfaces.ICMSContent(unique_id)
    group = zeit.content.image.interfaces.IImageGroup(video)
    image = group['{}.jpg'.format(img)]
    assert 'Bildschirmfoto-2015-01-22-um-09-27-07.jpg' in image.src
    assert image.mimeType == 'image/jpeg'
    assert image.image_pattern == 'brightcove-{}'.format(img)
    assert image.copyright is None
    assert image.caption.startswith(u'Er ist so groß wie ein siebenjähriges')
    assert image.title == u'Roboter Myon übernimmt Opernrolle'
    assert image.alt == u'Roboter Myon übernimmt Opernrolle'
    assert image.uniqueId == '{}/imagegroup/{}.jpg'.format(unique_id, img)


@pytest.mark.parametrize('img,size,res', [
    ('still', 460207, (580, 328)),
    ('thumbnail', 23420, (120, 67))
])
def test_video_imagegroup_should_set_local_image_fileobj(
        img, size, res, application):
    unique_id = 'http://xml.zeit.de/video/2015-01/3537342483001'
    video = zeit.cms.interfaces.ICMSContent(unique_id)
    group = zeit.content.image.interfaces.IImageGroup(video)
    image = group['{}.jpg'.format(img)]
    assert image.image.size == size
    assert image.image.getImageSize() == res


def test_video_imagegroup_should_fallback(
        application, workingcopy, monkeypatch, mockserver):
    unique_id = 'http://xml.zeit.de/video/2015-01/3537342483001'
    video = zeit.cms.interfaces.ICMSContent(unique_id)
    with zeit.cms.checkout.helper.checked_out(
            video, ignore_conflicts=True, events=False) as obj:
        obj.video_still = 'http://example.com/foo'
    group = zeit.content.image.interfaces.IImageGroup(video)
    assert group['still.jpg'].image.getImageSize() == (500, 300)

    with zeit.cms.checkout.helper.checked_out(
            video, ignore_conflicts=True, events=False) as obj:
        obj.video_still = 'http://fusel'
    group = zeit.content.image.interfaces.IImageGroup(video)
    assert group['still.jpg'].image.getImageSize() == (500, 300)

    with zeit.cms.checkout.helper.checked_out(
            video, ignore_conflicts=True, events=False) as obj:
        obj.video_still = None
    group = zeit.content.image.interfaces.IImageGroup(video)
    assert group['still.jpg'].image.getImageSize() == (500, 300)


def test_video_page_should_feature_sharing_images(testserver, testbrowser):
    doc = testbrowser(
        '{}/video/2015-01/3537342483001'.format(testserver.url)).document
    url = r'.*video/2015-01/3537342483001/imagegroup/.*/still.jpg'
    assert re.match(
        url, doc.xpath('//meta[@property="og:image"]/@content')[0])
    assert re.match(
        url, doc.xpath('//meta[@name="twitter:image:src"]/@content')[0])


def test_video_page_should_feature_schema_org_props(testserver, testbrowser):
    doc = testbrowser(
        '{}/video/2015-01/3537342483001'.format(testserver.url)).document
    assert doc.xpath('//meta[@itemprop="duration" and @content="PT436S"]')
    assert re.match(r'.*video/2015-01/3537342483001/imagegroup/.*/still.jpg',
                    doc.xpath('//meta[@itemprop="thumbnail"]/@content')[0])
    assert doc.xpath('//meta[@itemprop="duration" and @content="PT436S"]')


def test_video_page_should_print_out_video_headline(testserver, testbrowser):
    doc = testbrowser(
        '{}/video/2015-01/3537342483001'.format(testserver.url)).document
    assert [u'Künstliche Intelligenz',
            u': ',
            u'Roboter Myon übernimmt Opernrolle'
            ] == doc.xpath('//h1[@itemprop="headline"]/span/text()')


def test_video_page_should_render_video_description(testserver, testbrowser):
    doc = testbrowser(
        '{}/video/2015-01/3537342483001'.format(testserver.url)).document
    assert u'Er ist so groß wie ein siebenjähriges Kind und lernt noch' in (
        doc.xpath('//div[@itemprop="description"]/text()')[0])


def test_video_page_should_display_modified_date(testserver, testbrowser):
    doc = testbrowser(
        '{}/video/2015-01/3537342483001'.format(testserver.url)).document
    assert '22. Januar 2015, 10:27' in doc.xpath(
        '//time[@datetime]/text()')[0]


@pytest.mark.xfail(reason='Comment module is to be included on video pages.')
def test_video_page_should_output_zero_comment_count(testserver, testbrowser):
    doc = testbrowser(
        '{}/video/2015-01/3537342483001'.format(testserver.url)).document
    assert 'Noch keine Kommentare.' in doc.xpath(
        '//span[@itemprop="commentCount"]/text()')[0]
    assert doc.xpath('//meta[@itemprop="commentCount" and @content="0"]')


@pytest.mark.xfail(reason='Comment module is to be included on video pages.')
def test_video_page_should_output_comment_count_number(
        testserver, testbrowser, monkeypatch):
    attr = {'comment_count': 7, 'pages': {'title', 'meh'}, 'headline': 'bar'}
    monkeypatch.setattr(zeit.web.site.view_video.Video, 'comments', attr)
    doc = testbrowser(
        '{}/video/2015-01/3537342483001'.format(testserver.url)).document
    assert 'bar' in doc.xpath('//span[@itemprop="commentCount"]/text()')[0]


def test_video_page_should_include_comment_section(testserver, testbrowser):
    doc = testbrowser(
        '{}/video/2015-01/3537342483001'.format(testserver.url)).document
    assert doc.xpath('//section[@class="comment-section" and @id="comments"]')


def test_video_comment_form_should_be_rendered(testserver, testbrowser):
    browser = testbrowser(
        '{}/video/2015-01/3537342483001/comment-form'.format(testserver.url))
    assert len(browser.cssselect('#comment-form')) == 1


def test_video_report_form_should_be_rendered(testserver, testbrowser):
    browser = testbrowser(
        '{}/video/2015-01/3537342483001/report-form'.format(testserver.url))
    assert len(browser.cssselect('#comment-form')) == 1


def test_video_page_should_embed_sharing_menu(testserver, testbrowser):
    browser = testbrowser(
        '{}/video/2015-01/3537342483001'.format(testserver.url))
    assert len(browser.cssselect('.sharing-menu .sharing-menu__title')) > 0
    assert len(browser.cssselect('.sharing-menu a.sharing-menu__link')) > 0


def test_video_page_video_iframe_should_exist(testserver, testbrowser):
    browser = testbrowser(
        '{}/video/2015-01/3537342483001'.format(testserver.url))
    assert len(browser.cssselect('.video-player__iframe')) > 0


def test_video_page_video_should_exist(selenium_driver, testserver):
    video_id = '3537342483001'

    driver = selenium_driver
    driver.get('{}/video/2015-01/{}'.format(testserver.url, video_id))

    iframe = driver.find_element_by_css_selector(
        '.video-player__iframe')
    driver.switch_to.frame(iframe)

    try:
        player = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '.video-js'))
        )
        assert player
    except TimeoutException:
        assert False, 'Video not visible within 20 seconds'


def test_video_page_adcontroller_code_is_embedded(testbrowser, monkeypatch):
    monkeypatch.setattr(
        zeit.web.core.view.Base, 'enable_third_party_modules', tpm)

    browser = testbrowser('/video/2015-01/3537342483001')
    assert len(browser.cssselect('#ad-desktop-7')) == 1


def test_video_page_adcontroller_js_var_isset(
        selenium_driver, testserver, monkeypatch):
    monkeypatch.setattr(
        zeit.web.core.view.Base, 'enable_third_party_modules', tpm)
    driver = selenium_driver
    driver.get('{}/video/2015-01/3537342483001'.format(testserver.url))
    try:
        selector = 'body[data-adDeliveryType="adcontroller"]'
        driver.find_element_by_css_selector(selector)
    except:
        pytest.skip("not applicable due to oldschool ad configuration")

    adctrl = driver.execute_script("return typeof window.AdController")
    assert adctrl == "object"


# TODO: iFrame (?) wird eingebunden auf großen Bildschirmen
# TODO: iFrame (?) wird nicht eingebunden auf kleinen Bildschirmen
# TODO: CSS_SELECTOR trifft nicht unsere aktuelle HTML Struktur #fixme
# => Wobei, beide Tests gehören eher nach banner.py.
#    Wenn wir hier den JS Code und Wrapper haben und der andere Test für
#    Artikel-Banner läuft, können wir davon ausgehen dass er überall
#    funktioniert !?

@pytest.mark.skipif(True, reason='Fix me or I will always fail - after 20s')
def test_video_page_adcontroller_content_gets_included(
        selenium_driver, testserver, monkeypatch):

    driver = selenium_driver
    driver.get('{}/video/2015-01/3537342483001'.format(testserver.url))

    try:
        iframe = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                # syntax of expected condition is wrong
                # plus condition is not matching our current HTML structure
                (By.CSS_SELECTOR, 'ad__inner iframe'))
        )
        assert ('google_ads_iframe_' in iframe.get_attribute('id')) is True
    except TimeoutException:
        assert False, 'Iframe not found within 20 seconds'


def test_create_url_filter_should_append_seo_slug_to_all_video_links(
        application):
    video = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/video/2015-01/3537342483001')
    assert zeit.web.core.template.create_url(None, video) == (
        '/video/2015-01/3537342483001/kuenstliche-intelligenz'
        '-roboter-myon-uebernimmt-opernrolle')


def test_create_url_filter_should_handle_empty_supertitles(application):
    video = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/video/2014-01/1953013471001')
    assert zeit.web.core.template.create_url(None, video) == (
        '/video/2014-01/1953013471001/foto-momente'
        '-die-stille-schoenheit-der-polarlichter')


def test_video_page_should_redirect_to_slug_from_plain_id_url(
        testserver, testbrowser):
    path = '/video/2015-01/3537342483001'
    slug = '/kuenstliche-intelligenz-roboter-myon-uebernimmt-opernrolle'

    resp = requests.get(testserver.url + path, allow_redirects=False)
    assert resp.headers.get('Location', '') == testserver.url + path + slug

    resp = requests.get(testserver.url + path, allow_redirects=True)
    assert resp.url == testserver.url + path + slug


def test_video_page_should_redirect_to_correct_slug_from_faulty_slug(
        testserver, testbrowser):
    path = '/video/2015-01/3537342483001'
    slug = '/kuenstliche-intelligenz-roboter-myon-uebernimmt-opernrolle'

    resp = requests.get(testserver.url + path + '/foo', allow_redirects=False)
    assert resp.headers.get('Location', '') == testserver.url + path + slug

    resp = requests.get(testserver.url + path + '/foo', allow_redirects=True)
    assert resp.url == testserver.url + path + slug


def test_video_page_should_not_redirect_from_correct_slug_url(
        testserver, testbrowser):
    path = '/video/2015-01/3537342483001'
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
        'http://xml.zeit.de/gesellschaft/2015-02/crystal-meth-nancy-schmidt')
    assert not zeit.web.core.template.is_video(article)
