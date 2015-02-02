# -*- coding: utf-8 -*-
import mock
import pkg_resources
import pytest

import lxml.etree
import requests

import zeit.web.site.spektrum
import zeit.web.site.view_centerpage
import zeit.web.core.centerpage

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

screen_sizes = ((320, 480, True), (520, 960, True),
                (768, 1024, False), (980, 1024, False))


@pytest.fixture(scope='session', params=screen_sizes)
def screen_size(request):
    return request.param


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
        'http://localhost:6551/static/images/img1.jpg')


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


def test_spektrum_hp_feed_returns_values(application):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/parquet-teaser-setup')
    view = zeit.web.site.view_centerpage.Centerpage(cp, mock.Mock())
    feed = view.spektrum_hp_feed
    assert isinstance(feed, zeit.web.site.spektrum.HPFeed)


def test_spektrum_parquet_should_render_special_parquet_link(
        testbrowser, testserver):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/parquet-teaser-setup')
    view = zeit.web.site.view_centerpage.Centerpage(cp, mock.Mock())
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
