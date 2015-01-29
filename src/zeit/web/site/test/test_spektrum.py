# -*- coding: utf-8 -*-
import zeit.web.site.spektrum
import pkg_resources
import requests
import lxml.etree

def test_teaser_object_should_have_expected_attributes():
    url = pkg_resources.resource_filename(
        'zeit.web.core', 'data/spektrum/feed.xml')
    xml = lxml.etree.parse(url)

    iterator = iter(xml.xpath('/rss/channel/item'))
    item = next(iterator)

    teaser = zeit.web.site.spektrum.Teaser(item)

    assert teaser.teaserTitle == ' Ein Dinosaurier mit einem Hals wie ein Baukran'

