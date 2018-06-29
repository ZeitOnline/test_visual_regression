# -*- coding: utf-8 -*-
import mock
import pytest
import requests

import zeit.cms.interfaces
import zeit.content.video.video

import zeit.web.core.template
import zeit.web.site.view_video

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


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
    assert len(browser.cssselect('.sharing-menu a.sharing-menu__link')) > 0


def test_video_page_video_player_should_exist(testserver, testbrowser):
    browser = testbrowser('/zeit-online/video/3537342483001')
    assert len(browser.cssselect(
        '.js-videoplayer[data-video-id="3537342483001"]')) == 1


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


def test_video_teaser_should_display_byline(testbrowser):
    bylines = testbrowser('/zeit-online/video-teaser')\
        .cssselect("[class$='__byline']")
    assert len(bylines) == 7
    for value in bylines:
        # remove duplicated whitespace
        assert " ".join(value.text.split()) == 'Von Wenke Husmann'


def test_video_teaser_should_force_mobile_images(testbrowser):
    browser = testbrowser('/zeit-online/video-teaser')
    assert len(browser.cssselect('.teaser-small__media')) == 2
    assert len(browser.cssselect('.teaser-small__media--force-mobile')) == 2
    assert len(browser.cssselect('.teaser-small-minor__media')) == 1
    assert len(browser.cssselect(
        '.teaser-small-minor__media--force-mobile')) == 1


def test_video_single_page_should_display_byline(testbrowser):
    byline = testbrowser('/zeit-online/video/3537342483001')\
        .cssselect('.byline--on-videopage')
    assert len(byline) == 1
    temp = [byline[0].text]
    descendants = byline[0].iterdescendants()
    for i in descendants:
        temp.append(i.text)
    raw_inner_html = " ".join(temp).replace("\n", "")
    assert " ".join(raw_inner_html.split()) == 'Von Wenke Husmann'


def test_video_stage_main_should_display_byline(testbrowser):
    byline = testbrowser('zeit-online/video-stage') \
        .cssselect('.video-large__byline')
    assert len(byline) == 1
    assert " ".join(byline[0].text.split()) == 'Von Wenke Husmann'


def test_video_teaser_shows_video_length(testbrowser):
    select = testbrowser('zeit-online/video-stage').cssselect
    large = select('.video-large .video-text-playbutton__duration')
    assert len(large) == 1
    assert large[0].text == '1:54'

    small = select('.video-small .video-text-playbutton__duration')
    assert len(small) == 3
    assert small[0].text == '1:55'
    assert small[1].text == '7:16'
    assert small[2].text == '3:58'


def test_article_teaser_should_not_be_identified_as_video(application):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/image/crystal-meth-nancy-schmidt')
    assert not zeit.web.core.template.is_video(article)


def test_video_should_not_break_on_missing_still_image(
        testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.content.video.video.Video, 'video_still', None)
    testbrowser('/zeit-online/video/3537342483001')


def test_video_has_default_product_id(application, dummy_request):
    video = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/video/3537342483001')
    dummy_request.headers['X-SEO-Slug'] = (
        'kuenstliche-intelligenz-roboter-myon-uebernimmt-opernrolle')
    view = zeit.web.site.view_video.Video(video, dummy_request)
    assert view.product_id == 'zede'


def test_video_page_has_proper_article_tags(testbrowser):
    browser = testbrowser('/zeit-online/video/3537342483001')
    taglist = browser.cssselect('.article-tags')
    taglinks = browser.cssselect('.article-tags li a')
    assert len(taglist) == 1
    for taglink in taglinks:
        assert taglink.get('class').endswith('--video')


def test_video_page_should_contain_seo_slug_in_og_url(testbrowser):
    browser = testbrowser('/zeit-online/video/3537342483001')
    og_url = browser.xpath('head/meta[@property="og:url"]/@content')[0]
    assert og_url.endswith('intelligenz-roboter-myon-uebernimmt-opernrolle')


def test_video_comment_pagination_should_contain_seo_slug(
        application, dummy_request, tplbrowser):
    view = mock.Mock()
    view.comments.pages = {'pager': [1], 'current': 1, 'total': 3, 'sort': ''}
    view.context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/video/3537342483001')
    view.request = dummy_request
    browser = tplbrowser(
        'zeit.web.core:templates/inc/comments/pagination.html', view=view)
    link = browser.cssselect('.pager__button')[0].get('href')
    assert link == (
        'http://example.com/zeit-online/video/3537342483001/kuenstliche-'
        'intelligenz-roboter-myon-uebernimmt-opernrolle?page=2#comments')


def test_video_has_no_ads(testbrowser):
    browser = testbrowser('/zeit-online/article/video-ads')
    playerdata = browser.cssselect('.js-videoplayer')[0]
    assert playerdata.get('data-video-advertising') == ("withoutAds")


def test_expired_video_should_show_404(testserver):
    resp = requests.get('%s/zeit-online/video/3537342483002/' % testserver.url)
    assert resp.status_code == 404

    resp = requests.get(
        '%s/zeit-online/video/3537342483002/testdaten-abgelaufenes-video'
        % testserver.url)
    assert resp.status_code == 404


def test_video_page_has_no_print_menu(testbrowser):
    browser = testbrowser('/zeit-online/video/3537342483001')
    assert not browser.cssselect('.sharing-menu__item--printbutton')
    assert not browser.cssselect('.print-menu')


def test_video_has_correct_attributes(testbrowser):
    browser = testbrowser('/zeit-online/article/videos')
    players = browser.cssselect('.js-videoplayer')
    assert len(players) == 3

    assert players[0].get('data-video-id') == ("3035864892001")
    assert players[0].get('data-video-advertising') == ("withAds")
    assert players[0].get('data-video-playertype') == ("article")

    assert players[1].get('data-video-id') == ("3537342483001")
    assert players[1].get('data-video-advertising') == ("withoutAds")
    assert players[1].get('data-video-playertype') == ("article")

    assert players[2].get('data-video-id') == ("3089721834001")
    assert players[2].get('data-video-advertising') == ("withAds")
    assert players[2].get('data-video-playertype') == ("article")


def test_gdpr_dnt_cookie_works_on_videos(
        selenium_driver, testserver):
    driver = selenium_driver
    select = driver.find_elements_by_css_selector

    # add_cookie() only works for the domain of the last get(), sigh.
    driver.get('{}/zeit-online/article/simple'.format(testserver.url))
    driver.add_cookie({'name': 'gdpr', 'value': 'dnt'})

    driver.get('{}/zeit-online/article/video'.format(testserver.url))

    # HTML (the video itself) says "withAds"
    assert select('.js-videoplayer')[0].get_attribute(
        'data-video-advertising') == 'withAds'

    # JS (the cookie) loads the Player without Ads
    assert select('.video-player__videotag')[0].get_attribute(
        'data-player') == 'SJENxUNKe'


def test_video_should_have_playsinline_tag(selenium_driver, testserver):
    driver = selenium_driver
    select = driver.find_elements_by_css_selector
    driver.get('{}/zeit-online/article/videos'.format(testserver.url))
    players = select('.video-player__videotag')

    try:
        WebDriverWait(driver, 3).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, '.video-player__videotag')))
    except TimeoutException:
        assert False, 'videotag must be present'

    assert len(players) == 3

    assert select('.video-player__videotag')[0].get_attribute(
        'playsinline') == 'true'

    assert select('.video-player__videotag')[1].get_attribute(
        'playsinline') == 'true'

    assert select('.video-player__videotag')[2].get_attribute(
        'playsinline') == 'true'
