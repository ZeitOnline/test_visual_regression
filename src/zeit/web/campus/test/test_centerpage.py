# -*- coding: utf-8 -*-

import zeit.cms.interfaces
import zeit.web.core.interfaces
import pyramid.testing
import lxml.html


def test_campus_centerpage_should_produce_regular_topiclinks(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/centerpage/index')
    topiclink = zeit.web.core.interfaces.ITopicLink(context)
    labels = sorted(dict(topiclink).keys())
    assert labels == ['Ausdauersport', 'Bayerische Landesbank', 'Paul Auster']


def test_campus_article_should_import_topiclinks(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/article/simple')
    topiclink = zeit.web.core.interfaces.ITopicLink(context)
    labels = sorted(dict(topiclink).keys())
    assert labels == ['Ausdauersport', 'Bayerische Landesbank', 'Paul Auster']


def test_campus_article_should_use_default_topiclinks_of_hp(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/article/simple')
    article_topiclink = zeit.web.core.interfaces.ITopicLink(context)

    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/index')
    hp_topiclink = zeit.web.core.interfaces.ITopicLink(context)

    assert article_topiclink == hp_topiclink


def test_campus_centerpage_teaser_topic_is_rendered(jinja2_env):
    tpl = jinja2_env.get_template('zeit.web.campus:templates/centerpage.html')
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/centerpage/teaser-topic')
    request = pyramid.testing.DummyRequest(
        route_url=lambda x: 'http://foo.bar/',
        asset_host='',
        image_host='')
    request.route_url.return_value = 'http://foo.bar/'
    view = zeit.web.site.view_centerpage.Centerpage(content, request)
    view.meta_robots = ''
    view.canonical_url = ''
    html_str = tpl.render(view=view, request=request)
    html = lxml.html.fromstring(html_str)

    assert len(html.cssselect('.teaser-topic')) == 1
    assert len(html.cssselect('.teaser-topic-main')) == 1
    assert len(html.cssselect('.teaser-topic-item')) == 3
