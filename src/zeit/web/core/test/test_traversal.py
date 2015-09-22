import urllib2

import pyramid.request
import pytest

from zeit.cms.checkout.helper import checked_out
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


def test_dynamic_folder_traversal_should_rewrite_traversal_dictionary(
        application, dummy_request):
    initial = dict(
        context=zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/dynamic'),
        traversed=('dynamic',),
        view_name='adel-tawil',
        request=dummy_request)

    expected = dict(
        context=zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/dynamic/adel-tawil'),
        traversed=('dynamic', 'adel-tawil'),
        view_name='',
        request=dummy_request)

    resulting = zeit.web.core.traversal.RepositoryTraverser.invoke(**initial)
    assert resulting == expected


def test_dynamic_folder_traversal_should_allow_for_ranking_pagination(
        application, dummy_request):
    dummy_request.GET['p'] = '2'

    tdict = zeit.web.core.traversal.RepositoryTraverser.invoke(
        context=zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/dynamic'),
        traversed=('dynamic',),
        view_name='adel-tawil',
        request=dummy_request)

    area = tdict['context'].values()[0].values()[1]
    assert zeit.web.core.centerpage.get_area(area).page == 2


def test_preview_can_traverse_workingcopy_directly(my_traverser, workingcopy):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    with checked_out(content, temporary=False):
        req = pyramid.request.Request.blank('/wcpreview/zope.user/01')
        tdict = my_traverser(req)
        assert zeit.content.article.interfaces.IArticle.providedBy(
            tdict['context'])


def test_route_config_should_make_friedbert_surrender_to_blacklisted_routes(
        testbrowser):
    with pytest.raises(urllib2.HTTPError) as info:
        browser = testbrowser('/studium/rankings/index')
        assert browser.headers.get('X-Render-With')
    error = info.value
    assert error.getcode() == 303


@pytest.mark.parametrize('path, moved', [
    ('', '/index'),
    ('/', '/index'),
    ('/zeit-online', '/zeit-online/index'),
    ('/zeit-online/', '/zeit-online/index')])
def test_plain_folder_traversal_should_trigger_redirect_to_index(
        path, moved, application):

    tdict = dict(
        context=zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/' + path.lstrip('/')),
        traversed=tuple(path.split('/')),
        view_name='',
        request=pyramid.request.Request.blank(path))

    with pytest.raises(
            pyramid.httpexceptions.HTTPMovedPermanently) as redirect:
        zeit.web.core.traversal.RepositoryTraverser.invoke(**tdict)

    assert redirect.value.location.endswith(moved)
