import pyramid.scripts.pviews
import pyramid.request

import zeit.cms.interfaces


def test_instantarticle_view_should_match(application):
    pviews = pyramid.scripts.pviews.PViewsCommand([])
    request = pyramid.request.Request.blank(
        '/instantarticle/zeit-online/article/simple')
    request.registry = application.zeit_app.config.registry

    assert pviews._find_view(request).func_name == 'InstantArticle'


def test_fbia_view_should_match(application):
    pviews = pyramid.scripts.pviews.PViewsCommand([])
    registry = application.zeit_app.config.registry

    request = pyramid.request.Request.blank(
        '/fbia/zeit-online/article/simple')
    request.registry = registry

    assert pviews._find_view(request).func_name == 'InstantArticleTracking'


def test_amp_view_should_match(application):
    pviews = pyramid.scripts.pviews.PViewsCommand([])
    request = pyramid.request.Request.blank('/amp/zeit-online/article/simple')
    request.registry = application.zeit_app.config.registry
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/simple')

    assert pviews._find_view(request).match(context, request).func_name == (
        'AcceleratedMobilePageArticle')


def test_amp_view_should_redirect_if_flag_not_set(application):
    pviews = pyramid.scripts.pviews.PViewsCommand([])
    request = pyramid.request.Request.blank('/amp/zeit-online/article/01')
    request.registry = application.zeit_app.config.registry
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')

    assert pviews._find_view(request).match(context, request).func_name == (
        'redirect_amp_disabled')
