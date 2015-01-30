# -*- coding: utf-8 -*-
import zeit.web.site.spektrum
import pkg_resources
import lxml.etree

def test_spektrum_teaser_object_should_have_expected_attributes():
    url = pkg_resources.resource_filename(
        'zeit.web.core', 'data/spektrum/feed.xml')
    xml = lxml.etree.parse(url)

    iterator = iter(xml.xpath('/rss/channel/item'))
    item = next(iterator)

    teaser = zeit.web.site.spektrum.Teaser(item)

    assert teaser.teaserTitle == 'Ein Dinosaurier mit einem Hals wie ' + (
        'ein Baukran')
    assert teaser.teaserSupertitle == 'Qijianglong'
    assert teaser.teaserText ==u'Forscher entdecken ein China die ' + (
        u'\xc3\x9cberreste eines bisher unbekannten, ') + (
        u'langhalsigen Dinosauriers.')

    assert teaser._feed_image == 'http://www.spektrum.de/fm/912/' + (
        'thumbnails/85885_web.jpg.1616471.jpg')

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

def test_spektrum_title_should_be_colon_splitted():
    import zeit.web.site.spektrum

    xml_str = """
        <item>
        	<title><![CDATA[]]></title>
		<link><![CDATA[]]></link>
		<description><![CDATA[]]></description>
	</item>"""

    teaser = zeit.web.site.spektrum.Teaser(lxml.etree.fromstring(xml_str))
    assert teaser._split('supertitle: title')  == ('supertitle', 'title')

    assert teaser._split('') == ('', '')
    assert teaser._split('title') == ('title', '')



