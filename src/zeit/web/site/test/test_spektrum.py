# -*- coding: utf-8 -*-
import pkg_resources

import lxml.etree
import requests

import zeit.web.site.spektrum
import zeit.web.core.centerpage


def test_spektrum_teaser_object_should_have_expected_attributes():
    url = pkg_resources.resource_filename(
        'zeit.web.core', 'data/spektrum/feed.xml')
    xml = lxml.etree.parse(url)

    iterator = iter(xml.xpath('/rss/channel/item'))
    item = next(iterator)

    teaser = zeit.web.site.spektrum.Teaser(item)

    assert teaser.teaserTitle == (
        'Ein Dinosaurier mit einem Hals wie ein Baukran')
    assert teaser.teaserSupertitle == 'Qijianglong'
    assert teaser.teaserText == (
        u'Forscher entdecken ein China die \xc3\x9cberreste eines bisher '
        u'unbekannten, langhalsigen Dinosauriers.')
    assert teaser.feed_image == (
        'http://www.spektrum.de/fm/912/thumbnails/85885_web.jpg.1616471.jpg')


def test_spektrum_teaser_object_with_empty_values_should_not_break():
    xml_str = """
        <item>
            <title><![CDATA[]]></title>
            <link><![CDATA[]]></link>
            <description><![CDATA[]]></description>
        </item>"""

    xml = lxml.etree.fromstring(xml_str)
    teaser = zeit.web.site.spektrum.Teaser(xml)

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

    teaser = zeit.web.site.spektrum.Teaser(lxml.etree.fromstring(xml_str))
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
    image = zeit.web.site.spektrum.Teaser(xml).image
    assert image.mimeType == 'image/png'
    assert image.image_pattern == 'spektrum'
    assert image.caption == 'Puzzle puzzle puzzle'
    assert image.title == 'Puzzle'
    assert image.alt == 'Puzzle'
    assert image.uniqueId.endswith(path)
    assert image.image.size == 18805
    assert image.image.getImageSize() == (180, 120)
