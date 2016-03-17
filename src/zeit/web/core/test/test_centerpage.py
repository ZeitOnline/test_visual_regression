# -*- coding: utf-8 -*-

import zeit.cms.interfaces
import zeit.web.site.view_centerpage


def test_topic_teaser_contain_expected_structure(tplbrowser, dummy_request):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/topic-teaser')
    view = zeit.web.site.view_centerpage.Centerpage(context, dummy_request)
    area = view.regions[1][0]
    browser = tplbrowser('zeit.web.core:templates/inc/area/topic.html',
                         view=view, request=dummy_request, area=area)
    assert browser.cssselect('.teaser-topic')
    assert browser.cssselect('.teaser-topic__media')
    assert browser.cssselect('.teaser-topic-main')
    assert browser.cssselect('.teaser-topic-list')
    assert len(browser.cssselect('.teaser-topic-item')) == 3
