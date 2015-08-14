import pyramid.request

import zeit.content.cp.interfaces
import zeit.cms.interfaces

import zeit.web.core.article


def test_spektrum_feed_should_not_use_parallel_cp(my_traverser):
    req = pyramid.request.Request.blank(
        '/parallel_cps/index/rss-spektrum-flavoured')
    tdict = my_traverser(req)
    assert tdict['context'].uniqueId == (
        'http://xml.zeit.de/parallel_cps/index')


def test_rendered_xml_view_should_not_use_parallel_cp(my_traverser):
    req = pyramid.request.Request.blank(
        '/parallel_cps/index/xml')
    tdict = my_traverser(req)
    assert tdict['context'].uniqueId == (
        'http://xml.zeit.de/parallel_cps/index')


def test_feature_longform_should_be_discovered_during_traversal(my_traverser):
    req = pyramid.request.Request.blank('/feature/feature_longform')
    tdict = my_traverser(req)
    assert zeit.web.core.article.IFeatureLongform.providedBy(tdict['context'])


def test_parallel_cps_should_be_discovered_during_traversal(my_traverser):
    req = pyramid.request.Request.blank('/parallel_cps/index')
    tdict = my_traverser(req)
    assert tdict['context'].uniqueId == (
        'http://xml.zeit.de/parallel_cps/index.cp2015')
    assert zeit.content.cp.interfaces.ICenterPage.providedBy(tdict['context'])


def test_parallel_folders_should_be_discovered_during_traversal(my_traverser):
    req = pyramid.request.Request.blank('/parallel_cps/serie/index')
    tdict = my_traverser(req)
    assert tdict['context'].uniqueId == (
        'http://xml.zeit.de/parallel_cps/serie.cp2015/index')
    assert zeit.content.cp.interfaces.ICenterPage.providedBy(tdict['context'])
