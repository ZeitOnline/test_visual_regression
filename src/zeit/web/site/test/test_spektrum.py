# -*- coding: utf-8 -*-
import pkg_resources
import pytest
import re

import lxml.etree
import requests
import pyramid.testing

import zeit.web.site.area.spektrum
import zeit.web.site.view_centerpage
import zeit.web.core.centerpage


def test_spektrum_teaser_object_should_have_expected_attributes():
    url = pkg_resources.resource_filename(
        'zeit.web.core', 'data/spektrum/feed.xml')
    xml = lxml.etree.parse(url)

    iterator = iter(xml.xpath('/rss/channel/item'))
    item = next(iterator)

    teaser = zeit.web.site.area.spektrum.Teaser(item)

    assert teaser.teaserTitle == (
        'Ein Dinosaurier mit einem Hals wie ein Baukran')
    assert teaser.teaserSupertitle == 'Qijianglong'
    assert teaser.teaserText == (
        u'Forscher entdecken ein China die \xc3\x9cberreste eines bisher '
        u'unbekannten, langhalsigen Dinosauriers.')
    assert teaser.feed_image.endswith('spektrum/images/img1.jpg')


def test_spektrum_teaser_object_with_empty_values_should_not_break():
    xml_str = """
        <item>
            <title><![CDATA[]]></title>
            <link><![CDATA[]]></link>
            <description><![CDATA[]]></description>
        </item>"""

    xml = lxml.etree.fromstring(xml_str)
    teaser = zeit.web.site.area.spektrum.Teaser(xml)

    assert teaser.teaserSupertitle == ''
    assert teaser.teaserTitle == ''
    assert teaser.teaserText == ''
    assert teaser.image is None


def test_spektrum_title_should_be_colon_splitted():
    xml_str = """
        <item>
            <title><![CDATA[]]></title>
            <link><![CDATA[]]></link>
            <description><![CDATA[]]></description>
        </item>"""

    teaser = zeit.web.site.area.spektrum.Teaser(
        lxml.etree.fromstring(xml_str))
    assert teaser._split('supertitle: title') == ('supertitle', 'title')
    assert teaser._split('') == ('', '')
    assert teaser._split('title') == ('', 'title')
    assert teaser._split('supertitle:') == ('supertitle', '')
    assert teaser._split(':title') == ('', 'title')


def test_spektrum_image_should_have_expected_attributes(application):
    path = 'data/spektrum/images/pixabay146378.png'
    enclosure = pkg_resources.resource_filename('zeit.web.core', path)
    xml_str = """
        <item>
            <title><![CDATA[Puzzle]]></title>
            <link><![CDATA[]]></link>
            <description><![CDATA[Puzzle puzzle puzzle]]></description>
            <enclosure url="file://{}" length="18805" type="image/png"/>
        </item>""".format(enclosure)

    xml = lxml.etree.fromstring(xml_str)
    image = zeit.web.site.area.spektrum.Teaser(xml).image
    assert image.mimeType == 'image/png'
    assert image.image_pattern == 'spektrum'
    assert image.caption == 'Puzzle puzzle puzzle'
    assert image.title == 'Puzzle'
    assert image.alt == 'Puzzle'
    assert image.uniqueId.endswith(path)
    assert image.image.size == 18805
    assert image.image.getImageSize() == (180, 120)


def test_centerpage_recognizes_spektrum_cpextra(testserver):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/parquet-teaser-setup')
    view = zeit.web.site.view_centerpage.LegacyCenterpage(
        cp, pyramid.testing.DummyRequest())
    mods = view.region_list_parquet[1].values()[0].values()
    assert all(isinstance(
        t[0], zeit.web.site.area.spektrum.Teaser) for t in mods)


def test_spektrum_parquet_should_render_special_parquet_link(
        testbrowser, testserver):
    browser = testbrowser(
        '%s/zeit-online/parquet-teaser-setup' % testserver.url)
    teasers = browser.cssselect(
        '.parquet-meta__more.parquet-meta__more--spektrum')
    actual_amount = len(teasers)
    assert actual_amount == 1, (
        'Parquet row does not display the right amount of spektrum.')
    text = teasers[0].text
    assert "Aktuelles aus der Welt von Wissenschaft und Forschung:" in text, (
        'Spektrum link has not the correct text')


def test_sprektrum_parquet_should_display_meta_more(
        selenium_driver, testserver):
    driver = selenium_driver
    driver.get('%s/zeit-online/parquet-teaser-setup' % testserver.url)

    more_link = driver.find_element_by_css_selector(
        '.parquet-meta__more--spektrum')

    driver.set_window_size(520, 960)
    assert not more_link.is_displayed(), (
        'Parquet more-link should not be displayed on mobile.')

    driver.set_window_size(980, 1024)
    assert more_link.is_displayed(), (
        'Parquet more-link must be displayed on desktop.')


def test_spektrum_area_should_render_empty_if_feed_unavailable(
        testbrowser, testserver, monkeypatch):
    monkeypatch.setattr(zeit.web.site.area.spektrum, 'HPFeed', list)
    browser = testbrowser(
        '%s/zeit-online/parquet-teaser-setup' % testserver.url)
    assert not browser.cssselect('.cp-area--spektrum')


def test_spektrum_cooperation_route_should_be_configured(testserver):
    assert requests.get('%s/spektrum-kooperation' % testserver.url).ok


@pytest.mark.parametrize('index,slug', [
    (0, ('hp.centerpage.teaser.parquet.42.1.a|'
         'http://www.spektrum.de/astronomie')),
    (1, ('hp.centerpage.teaser.parquet.42.1.b|'
         'http://www.spektrum.de/biologie')),
    (2, ('hp.centerpage.teaser.parquet.42.1.c|'
         'http://www.spektrum.de/psychologie-hirnforschung'))
])
def test_spektrum_topic_links_should_produce_correct_tracking_slugs(
        index, slug, testbrowser, testserver):
    browser = testbrowser(
        '%s/spektrum-kooperation?parquet-position=42' % testserver.url)
    topiclink = browser.cssselect('.parquet-meta__topic-link')[index]
    assert topiclink.get('id') == slug


@pytest.mark.parametrize('index,img_slug,title_slug', [
    (0, 'hp.centerpage.teaser.parquet.43.3.a.image',
        'hp.centerpage.teaser.parquet.43.3.a.title'),
    (1, 'hp.centerpage.teaser.parquet.43.3.b.image',
        'hp.centerpage.teaser.parquet.43.3.b.title'),
    (2, 'hp.centerpage.teaser.parquet.43.3.c.image',
        'hp.centerpage.teaser.parquet.43.3.c.title')
])
def test_spektrum_teasers_should_produce_correct_tracking_slugs(
        index, img_slug, title_slug, testbrowser, testserver):
    browser = testbrowser(
        '%s/spektrum-kooperation?parquet-position=43' % testserver.url)
    img = browser.cssselect('.teaser-small__media-link')[index]
    assert img.get('id').startswith(img_slug)
    title = browser.cssselect('.teaser-small__combined-link')[index]
    assert title.get('id').startswith(title_slug)


def test_rss_feed_of_cp_has_requested_format(testserver):
    feed_path = '/centerpage/index/rss-spektrum-flavoured'
    res = requests.get(
        testserver.url + feed_path, headers={'Host': 'newsfeed.zeit.de'})
    assert res.headers['Content-Type'].startswith('application/rss+xml')
    feed = res.text
    assert '<atom:link href="http://newsfeed.zeit.de%s"' % feed_path in feed
    assert '<link>http://www.zeit.de/centerpage/article_image_asset?' in feed
    assert ('wt_zmc=koop.ext.zonaudev.spektrumde.feed.'
            'article-image-asset.bildtext.link.x' in feed)
    assert re.search(
        '<enclosure .* url="http://newsfeed.zeit.de/centerpage/katzencontent/',
        feed)


def test_spektrum_also_renders_on_ng_centerpages(testbrowser, testserver):
    browser = testbrowser('/zeit-online/parquet')
    rows = browser.cssselect('.cp-region--parquet .cp-area--spektrum')
    assert len(rows) == 1, (
        'Parquet row does not display the right amount of spektrum.')
    links = rows[0].find_class('parquet-meta__more--spektrum')
    assert len(links) == 1, 'link to www.spektrum.de is missing'
    text = links[0].text
    assert "Aktuelles aus der Welt von Wissenschaft und Forschung:" in text, (
        'Spektrum link has not the correct text')
