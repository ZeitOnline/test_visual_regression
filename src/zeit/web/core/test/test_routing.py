import urllib2

import pyramid.request
import pytest
import requests
import zope.component

from zeit.cms.checkout.helper import checked_out
import zeit.content.cp.interfaces
import zeit.cms.interfaces

import zeit.web
import zeit.web.core.routing


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

    resulting = zeit.web.core.routing.RepositoryTraverser.invoke(**initial)
    assert resulting == expected


def test_dynamic_folder_traversal_should_allow_for_ranking_pagination(
        application, dummy_request, data_solr):
    dummy_request.GET['p'] = '2'

    tdict = zeit.web.core.routing.RepositoryTraverser.invoke(
        context=zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/dynamic'),
        traversed=('dynamic',),
        view_name='adel-tawil',
        request=dummy_request)

    area = tdict['context'].values()[1].values()[0]
    assert zeit.web.core.centerpage.get_area(area).page == 2


def test_preview_can_traverse_workingcopy_directly(my_traverser, workingcopy):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    with checked_out(content, temporary=False):
        req = pyramid.request.Request.blank('/wcpreview/zope.user/01')
        tdict = my_traverser(req)
        assert zeit.content.article.interfaces.IArticle.providedBy(
            tdict['context'])


def test_routesmapper_should_make_friedbert_surrender_to_blacklisted_routes(
        testbrowser):
    with pytest.raises(urllib2.HTTPError) as info:
        browser = testbrowser('/studium/rankings/index')
        assert browser.headers.get('X-Render-With') == 'default'
        assert info.value.getcode() == 501


def test_routesmapper_should_make_friedbert_unblacklist_newsfeed_host(
        testserver):
    resp = requests.get(testserver.url + '/angebote/printkiosk/index',
                        headers={'Host': 'newsfeed.zeit.de'})
    assert 'X-Render-With' not in resp.headers


def test_blacklist_entry_should_match_everything_but_image_urls(testbrowser):
    with pytest.raises(urllib2.HTTPError) as info:
        resp = testbrowser('/angebote/autosuche/foo/bar/index')
        assert resp.headers.get('X-Render-With') == 'default'
    assert info.value.getcode() == 501

    with pytest.raises(urllib2.HTTPError) as info:
        resp = testbrowser('/angebote/autosuche/foo/bar/my_logo')
        assert resp.headers.get('X-Render-With') == 'default'
    assert info.value.getcode() == 501

    with pytest.raises(urllib2.HTTPError) as info:
        testbrowser('/angebote/autosuche/foo/bar/wide__123x456')
    assert info.value.getcode() == 404


def test_errors_on_blacklist_configuration_should_be_ignored(
        testserver, monkeypatch):
    monkeypatch.setattr(
        zeit.web.core.routing.BlacklistSource, 'getValues', None)
    zeit.web.core.routing.BlacklistSource()(None)
    # Just make sure blacklist compilation failures won't breaking anything.
    assert requests.get(testserver.url + '/index').ok is True


@pytest.mark.parametrize('path, moved', [
    ('', '/index'),
    ('/', '/index'),
    ('/zeit-online', '/zeit-online/index'),
    ('/zeit-magazin/', '/zeit-magazin/index'),
    ('/zeit-magazin', '/zeit-magazin/index'),
    ('/campus/', '/campus/index'),
    ('/campus', '/campus/index'),
    ('/zeit-online/', '/zeit-online/index'),
    ('/zeit-online/?wt_param=12001', '/zeit-online/index?wt_param=12001'),
    ('/zeit-online?page=25#static', '/zeit-online/index?page=25#static')])
def test_plain_folder_traversal_should_trigger_redirect_to_index(
        path, moved, application):

    tdict = dict(
        context=zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/' + path.split('?')[0].lstrip('/')),
        traversed=tuple(path.split('?')[0].split('/')),
        view_name='',
        request=pyramid.request.Request.blank(path))

    with pytest.raises(
            pyramid.httpexceptions.HTTPMovedPermanently) as redirect:
        zeit.web.core.routing.RepositoryTraverser.invoke(**tdict)

    assert redirect.value.location.endswith(moved)


@pytest.mark.parametrize('path, moved', [
    ('/dynamic', '/dynamic/index'),
    ('/dynamic/', '/dynamic/index'),
    ('/dynamic/?wt_param=12001', '/dynamic/index?wt_param=12001'),
    ('/dynamic?page=25#static', '/dynamic/index?page=25#static')])
def test_dynamic_folder_traversal_should_trigger_redirect_to_index(
        path, moved, application):

    tdict = dict(
        context=zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/dynamic'),
        traversed=tuple(path.split('?')[0].split('/')),
        view_name='',
        request=pyramid.request.Request.blank(path))

    with pytest.raises(
            pyramid.httpexceptions.HTTPMovedPermanently) as redirect:
        zeit.web.core.routing.RepositoryTraverser.invoke(**tdict)

    assert redirect.value.location.endswith(moved)


def test_view_config_should_apply_custom_defaults(monkeypatch):
    defaults = {'foo': 42, 'bar': False}
    monkeypatch.setattr(zeit.web.view_config, '__global_defaults__', defaults)

    decorator = zeit.web.view_config(bar=True)

    assert decorator.foo == 42
    assert decorator.bar is True


def test_host_restriction_predicate_validates_argument(application):
    Predicate = zeit.web.core.routing.HostRestrictionPredicate  # NOQA

    with pytest.raises(TypeError):
        Predicate(object(), {})
    with pytest.raises(TypeError):
        Predicate(('foo', object()), {})

    assert Predicate('foo', {}).value == ('foo',)
    assert Predicate(None, {}).value is False
    assert Predicate(True, {}).value is True
    assert Predicate(False, {}).value is False
    assert Predicate(('foo', 'bar'), {}).value == ('foo', 'bar')


def test_host_restriction_predicate_registers_host_in_settings(application):
    zeit.web.core.routing.HostRestrictionPredicate('foo', {})
    zeit.web.core.routing.HostRestrictionPredicate(('foo', 'bar'), {})

    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    assert conf['restricted_hosts'].issuperset({'foo', 'bar'})


def test_host_restriction_predicate_hashes_with_argument(application):
    pred = zeit.web.core.routing.HostRestrictionPredicate(('foo', 'bar'), {})
    assert pred.text() == pred.phash() == "host_restriction = ('foo', 'bar')"


def test_host_restriction_predicate_is_true_for_exempt_views(dummy_request):
    # Make sure we have at least one claimed host
    zeit.web.core.routing.HostRestrictionPredicate('one', {})

    pred = zeit.web.core.routing.HostRestrictionPredicate(False, {})
    assert pred({}, dummy_request) is True
    pred = zeit.web.core.routing.HostRestrictionPredicate(None, {})
    assert pred({}, dummy_request) is True


def test_host_restriction_predicate_is_true_on_unclaimed_host(dummy_request):
    zeit.web.core.routing.HostRestrictionPredicate('one', {})

    dummy_request.headers['host'] = 'two.zeit.de'
    pred = zeit.web.core.routing.HostRestrictionPredicate(True, {})
    assert pred({}, dummy_request) is True


def test_host_restriction_predicate_is_false_on_claimed_host(dummy_request):
    zeit.web.core.routing.HostRestrictionPredicate('one', {})

    dummy_request.headers['host'] = 'one.zeit.de'
    pred = zeit.web.core.routing.HostRestrictionPredicate(True, {})
    assert pred({}, dummy_request) is False


def test_host_restriction_predicate_is_true_on_matching_host(dummy_request):
    zeit.web.core.routing.HostRestrictionPredicate('one', {})

    dummy_request.headers['host'] = 'two.zeit.de'
    pred = zeit.web.core.routing.HostRestrictionPredicate('two', {})
    assert pred({}, dummy_request) is True


def test_host_restriction_predicate_is_false_on_divergent_host(dummy_request):
    zeit.web.core.routing.HostRestrictionPredicate('one', {})

    dummy_request.headers['host'] = 'one.zeit.de'
    pred = zeit.web.core.routing.HostRestrictionPredicate('two', {})
    assert pred({}, dummy_request) is False
