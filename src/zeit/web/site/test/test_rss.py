# -*- coding: utf-8 -*-
import mock
import pkg_resources
import re

import lxml.etree
import requests

import zeit.web.core.centerpage
import zeit.web.core.template
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


def test_spektrum_supertitle_should_be_extracted_from_category():
    xml_str = """
        <item>
            <category><![CDATA[Lorem ipsum]]></category>
        </item>"""

    teaser = zeit.web.site.area.spektrum.Link(lxml.etree.fromstring(xml_str))
    assert teaser.supertitle == 'Lorem ipsum'


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

    image = zeit.web.core.template.get_image(link, variant_id='wide')
    assert image.path.endswith('{}/wide'.format(path))
    assert image.caption == 'Puzzle puzzle puzzle'
    assert image.title == 'Puzzle'
    assert image.alt == 'Puzzle'


def test_rss_images_should_render(testbrowser):
    browser = testbrowser('/zeit-online/parquet-feeds')
    assert browser.cssselect('.cp-area--zett article img')


def test_spektrum_parquet_should_render_special_parquet_link(testbrowser):
    browser = testbrowser('/zeit-online/parquet-feeds')
    teasers = browser.cssselect(
        '.parquet-meta__more.parquet-meta__more--spektrum')
    actual_amount = len(teasers)
    assert actual_amount == 1, (
        'Parquet row does not display the right amount of spektrum.')
    text = teasers[0].text
    assert "Aktuelles aus der Welt von Wissenschaft und Forschung:" in text, (
        'Spektrum link has not the correct text')


def test_spektrum_parquet_should_display_meta_more(
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
        testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.site.area.rss.RSSArea, 'values', list)
    browser = testbrowser('/zeit-online/parquet-feeds')
    assert not browser.cssselect('.teaser-small')


def test_rss_feed_of_cp_has_requested_format(testserver):
    feed_path = '/zeit-magazin/centerpage/index/rss-spektrum-flavoured'
    res = requests.get(
        testserver.url + feed_path, headers={'Host': 'newsfeed.zeit.de'})
    assert res.headers['Content-Type'].startswith('application/rss+xml')
    feed = res.text
    assert '<atom:link href="http://newsfeed.zeit.de%s"' % feed_path in feed
    assert ('<link>http://www.zeit.de/zeit-magazin/'
            'centerpage/article_image_asset?' in feed)
    assert ('wt_zmc=koop.ext.zonaudev.spektrumde.feed.'
            'article-image-asset.bildtext.link.x' in feed)
    assert re.search(
        '<enclosure.*url="http://newsfeed.zeit.de/'
        'zeit-magazin/centerpage/katzencontent/',
        feed)


def test_spektrum_also_renders_on_ng_centerpages(testbrowser):
    browser = testbrowser('/zeit-online/parquet')
    rows = browser.cssselect('.cp-region--parquet .cp-area--spektrum')
    assert len(rows) == 1, (
        'Parquet row does not display the right amount of spektrum.')
    links = rows[0].find_class('parquet-meta__more--spektrum')
    assert len(links) == 1, 'link to www.spektrum.de is missing'
    text = links[0].text
    assert "Aktuelles aus der Welt von Wissenschaft und Forschung:" in text, (
        'Spektrum link has not the correct text')
