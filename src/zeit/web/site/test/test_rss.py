# -*- coding: utf-8 -*-
import mock
import pkg_resources
import re

import lxml.etree
import requests

import zeit.web.core.centerpage
import zeit.web.site.area.rss
import zeit.web.site.area.spektrum
import zeit.web.site.area.zett
import zeit.web.site.view_centerpage


def test_spektrum_teaser_object_should_have_expected_attributes():
    url = pkg_resources.resource_filename(
        'zeit.web.core', 'data/spektrum/feed.xml')
    xml = lxml.etree.parse(url)
    item = next(iter(xml.xpath('/rss/channel/item')))
    teaser = zeit.web.site.area.spektrum.Link(item)

    assert teaser.teaserTitle == (
        'Ein Dinosaurier mit einem Hals wie ein Baukran')
    assert teaser.teaserSupertitle == 'Qijianglong'
    assert teaser.teaserText == (
        u'Forscher entdecken ein China die \xc3\x9cberreste eines bisher '
        u'unbekannten, langhalsigen Dinosauriers.')
    assert teaser.image_url.endswith('spektrum/images/img1.jpg')


def test_rss_link_object_with_empty_values_should_not_break():
    xml_str = """
        <item>
            <title><![CDATA[]]></title>
            <link><![CDATA[]]></link>
            <description><![CDATA[]]></description>
        </item>"""

    xml = lxml.etree.fromstring(xml_str)
    teaser = zeit.web.site.area.rss.RSSLink(xml)

    assert teaser.teaserSupertitle is None
    assert teaser.teaserTitle is ''
    assert teaser.teaserText is ''
    assert teaser.image_url is None


def test_spektrum_title_should_be_colon_splitted():
    xml_str = """
        <item>
            <title><![CDATA[supertitle: title]]></title>
        </item>"""

    teaser = zeit.web.site.area.spektrum.Link(
        lxml.etree.fromstring(xml_str))
    assert teaser.title == 'title'
    assert teaser.supertitle == 'supertitle'


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

    area = mock.Mock()
    area.kind = 'spektrum'
    xml = lxml.etree.fromstring(xml_str)
    link = zeit.web.site.area.spektrum.Link(xml)
    link.__parent__ = area

    group = zeit.content.image.interfaces.IImages(link).image
    image = group['wide__180x120']
    assert image.mimeType == 'image/jpeg'
    assert group.uniqueId.endswith(path)
    assert image.size == 19599
    assert image.getImageSize() == (180, 120)

    meta = zeit.content.image.interfaces.IImageMetadata(group)
    assert meta.caption == 'Puzzle puzzle puzzle'
    assert meta.title == 'Puzzle'
    assert meta.alt == 'Puzzle'


def test_spektrum_parquet_should_render_special_parquet_link(
        testbrowser, testserver):
    browser = testbrowser(
        '%s/zeit-online/parquet-feeds' % testserver.url)
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
    driver.get('%s/zeit-online/parquet-feeds' % testserver.url)

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
    monkeypatch.setattr(zeit.web.site.area.rss.RSSArea, 'values', list)
    browser = testbrowser(
        '%s/zeit-online/parquet-feeds' % testserver.url)
    assert not browser.cssselect('.teaser-small')


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
