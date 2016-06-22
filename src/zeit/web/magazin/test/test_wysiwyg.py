# -*- coding: utf-8 -*-
from zeit.cms.interfaces import ICMSContent
from zeit.wysiwyg.interfaces import IHTMLContent
import lxml.objectify
import mock
import pyramid.testing


def test_accessing_html_body_works(application):
    gallery = ICMSContent(
        'http://xml.zeit.de/galerien/bg-automesse-detroit-2014-usa')
    html_content = IHTMLContent(gallery)
    registry = pyramid.registry.Registry('testing', bases=(
        application.zeit_app.config.registry,))
    with mock.patch.object(html_content, 'get_tree') as get_tree:
        get_tree.return_value = lxml.objectify.XML(
            '<text><a href="http://xml.zeit.de/zeit-magazin/article/01">foo</a></text>')
        with pyramid.testing.testConfig(
                registry=registry,
                hook_zca=False, request=pyramid.testing.DummyRequest()):
            assert ('<a href="http://example.com/zeit-magazin/article/01">foo</a>\n' ==
                    html_content.html)
