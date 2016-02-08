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


def test_cp_should_have_buzz_module(
        testserver, testbrowser):
    browser = testbrowser(
        '%s/zeit-magazin/test-cp-2015/buzz' % testserver.url)
    assert '<section class="buzzboard">' in browser.contents
    assert '<table class="buzzboard__table' in browser.contents
    assert '<div class="buzzboard__container">' in browser.contents


def test_get_reaches_from_centerpage_view(application):
    settings = zope.component.queryUtility(zeit.web.core.interfaces.ISettings)
    request = mock.Mock()
    request.registry.settings.community_host = settings['community_host']
    request.registry.settings.linkreach_host = settings['linkreach_host']
    request.registry.settings.node_comment_statistics = settings[
        'node_comment_statistics']

    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/test-cp-2015/buzz')
    block = zeit.web.core.utils.find_block(
        cp, module='zmo-mostread')
    module = zeit.web.core.template.get_module(block)
    buzz = module.reach

    buzz_views = buzz.get_views(section='zeit-magazin')[1].score
    buzz_facebook = buzz.get_social(
        facet='facebook', section='zeit-magazin')[1].score
    buzz_comments = buzz.get_comments(section='zeit-magazin')[1].score

    assert buzz_views == 69167
    assert buzz_facebook == 408
    assert buzz_comments == 461


def test_teaser_square_large_has_correct_markup(testbrowser):
    browser = testbrowser('/centerpage/lebensart')
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
    assert supertitle.text.strip() == 'Article Image Asset Spitzmarke'
    assert title.text.strip() == 'Article Image Asset Titel'
    assert u'Dies k\u00F6nnte' in subtitle.text.strip()
    assert re.search('/centerpage/katzencontent/square',
                     img.get('src'))
    assert img.get('alt') == 'Die ist der Alttest'


def test_teaser_square_large_light_has_correct_markup(testbrowser):
    browser = testbrowser('/centerpage/lebensart-2')
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
    assert supertitle.text.strip() == 'Article Image Asset Spitzmarke'
    assert title.text.strip() == 'Article Image Asset Titel'
    assert u'Dies k\u00F6nnte' in subtitle.text.strip()
    assert re.search('/centerpage/katzencontent/square',
                     img.get('src'))
    assert img.get('alt') == 'Die ist der Alttest'


def test_teaser_landscape_small_has_correct_markup(testbrowser):
    browser = testbrowser('/zeit-magazin/test-cp/test-cp-zmo')
    element = browser.cssselect('.teaser-landscape-small')

    text_wrap = element[0].cssselect('.teaser-landscape-small__text')
    link_wrap = element[0].cssselect('a')
    image_wrap = element[0].cssselect('.teaser-landscape-small__media')
    supertitle = element[0].cssselect('.teaser-landscape-small__kicker')[0]
    title = element[0].cssselect('.teaser-landscape-small__title')[0]
    subtitle = element[0].cssselect('.teaser-landscape-small__subtitle')[0]
    img = element[0].cssselect('img')[0]

    assert len(text_wrap) != 0
    assert len(link_wrap) == 1
    assert len(image_wrap) != 0
    assert supertitle.text.strip() == u'Kochen für Gäste'
    assert title.text.strip() == 'Heimlich vegetarisch'
    assert u'Wenn Gäste kommen,' in subtitle.text.strip()
    assert re.search('pistazienparfait/wide__822x462',
                     img.get('src'))
    assert img.get('alt') == 'Das Pistazienparfait wird verspeist'


def test_teaser_gallery_upright_has_correct_markup(testbrowser):
    browser = testbrowser('/centerpage/lebensart')
    element = browser.cssselect('.teaser-gallery-upright')

    text_wrap = element[0].cssselect('.teaser-gallery-upright__text')
    link_wrap = element[0].cssselect('a')
    icon = element[0].cssselect('.icon-galerie-icon-white')
    img = element[0].cssselect('img')[0]
    image_pattern = 'katzencontent/portrait__612x816'
    assert len(text_wrap) != 0
    assert len(link_wrap) >= 1
    assert len(icon) == 1
    assert re.search(image_pattern, img.get('src'))
    assert img.get('alt') == 'Die ist der Alttest'


def test_teaser_upright_large_has_correct_markup(testbrowser):
    browser = testbrowser('zeit-magazin/test-cp/test-cp-large-teaser')
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
    assert supertitle.text.strip() == u'Article Image Asset Spitzmarke'
    assert title.text.strip() == 'Article Image Asset Titel'
    assert u'Dies könnte' in subtitle.text.strip()
    assert re.search('katzencontent/portrait__612x816',
                     img.get('src'))
    assert img.get('alt') == 'Die ist der Alttest'


def test_teaser_landscape_large_has_correct_markup(testbrowser):
    browser = testbrowser('/zeit-magazin/test-cp/test-cp-zmo-3')
    element = browser.cssselect('.teaser-landscape-large')

    text_wrap = element[0].cssselect('.teaser-landscape-large__text')
    link_wrap = element[0].cssselect('a')
    supertitle = element[0].cssselect(
        '.teaser-landscape-large__kicker')[0]
    title = element[0].cssselect('.teaser-landscape-large__title')[0]
    subtitle = element[0].cssselect('.teaser-landscape-large__subtitle')[0]

    assert len(text_wrap) != 0
    assert len(link_wrap) == 1
    assert supertitle.text.strip() == u'Serie Gesellschaftskritik'
    assert title.text.strip() == u'Über schlechte Laune'
    assert 'Grumpy Cat' in subtitle.text.strip()


def test_teaser_landscape_large_photo_has_correct_markup(testbrowser):
    browser = testbrowser('/zeit-magazin/test-cp/test-cp-zmo-2')
    element = browser.cssselect('.teaser-landscape-large-photo')

    text_wrap = element[0].cssselect('.teaser-landscape-large-photo__text')
    link_wrap = element[0].cssselect('a')
    supertitle = element[0].cssselect(
        '.teaser-landscape-large-photo__kicker')[0]
    title = element[0].cssselect('.teaser-landscape-large-photo__title')[0]

    assert len(text_wrap) != 0
    assert len(link_wrap) == 1
    assert supertitle.text.strip() == u'Serie Gesellschaftskritik'
    assert title.text.strip() == u'Über schlechte Laune'


def test_teaser_fullwidth_with_video_has_correct_markup(
        testbrowser, testserver):
    browser = testbrowser('/zeit-magazin/teaser-fullwidth')
    teaser = browser.cssselect('.teaser-fullwidth')[2]

    vid_wrap = teaser.cssselect('.teaser-fullwidth__media')[0]
    img = teaser.cssselect('img')[0]
    title_wrap = teaser.cssselect('header')[0]
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
    assert len(a) == 1


def test_teaser_fullwidth_light_with_video_has_correct_markup(
        testbrowser, testserver):
    browser = testbrowser('/zeit-magazin/teaser-fullwidth')
    teaser = browser.cssselect('.teaser-fullwidth--light')[1]

    vid_wrap = teaser.cssselect('.teaser-fullwidth__media')[0]
    img = teaser.cssselect('img')[0]
    title_wrap = teaser.cssselect('header')[0]
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
    assert len(a) == 1


def test_teaser_fullwidth_with_image_has_correct_markup(
        testbrowser, testserver):
    browser = testbrowser('/zeit-magazin/teaser-fullwidth')
    teaser = browser.cssselect('.teaser-fullwidth')[0]

    img_wrap = teaser.cssselect('.teaser-fullwidth__media')
    img = teaser.cssselect('img')[0]
    title_wrap = teaser.cssselect('header')
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
    assert len(a) == 1


def test_teaser_fullwidth_light_with_image_has_correct_markup(
        testbrowser, testserver):
    browser = testbrowser('/zeit-magazin/test-cp/test-cp-zmo-2')
    teaser = browser.cssselect('.teaser-fullwidth--light')[0]

    img_wrap = teaser.cssselect('.teaser-fullwidth__media')
    img = teaser.cssselect('img')[0]
    title_wrap = teaser.cssselect('header')
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
    assert len(a) == 1


def test_teaser_print_cover_has_correct_markup(testbrowser):
    browser = testbrowser('/zeit-magazin/index')
    element = browser.cssselect('.teaser-print-cover')[0]

    text_wrap = element.cssselect('.teaser-print-cover__text')
    link_wrap = element.cssselect('a')
    image_wrap = element.cssselect('.teaser-print-cover__media')
    supertitle = element.cssselect('.teaser-print-cover__kicker')[0]
    title = element.cssselect('.teaser-print-cover__title')[0]
    img = element.cssselect('img')[0]

    assert len(text_wrap) != 0
    assert len(link_wrap) == 1
    assert len(image_wrap) != 0
    assert supertitle.text.strip() == 'ZEITmagazin'
    assert 'Das neue Heft' in title.text.strip()
    assert re.search('heft/portrait__612x816',
                     img.get('src'))


def test_teaser_should_have_comment_count(
        mockserver_factory, testserver, testbrowser):

    cp_counts = """<?xml version="1.0" encoding="UTF-8"?>
    <nodes>
         <node comment_count="129"
               url="/zeit-magazin/article/essen-geniessen-spargel-lamm"/>
    </nodes>
    """
    mockserver_factory(cp_counts)
    browser = testbrowser(
        '%s/zeit-magazin/test-cp/test-cp-zmo' % testserver.url)
    counts = browser.cssselect('.icon-comments-count')
    assert int(counts[0].text) == 129
