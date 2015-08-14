import mock

import pyramid.scripts.pviews

import zeit.cms.interfaces

import zeit.web.site.view_centerpage


def test_custom_predicate_should_only_match_website_content(application):
    pviews = pyramid.scripts.pviews.PViewsCommand([])
    registry = application.zeit_app.config.registry
    views = pviews._find_view('/centerpage/zeitonline', registry).views

    # Just a helper, since the position in pviews in unpredictable
    def zon_view(pviews):
        for view in pviews:
            if view[1].__dict__['__original_view__'] == (
                    zeit.web.site.view_centerpage.LegacyCenterpage):
                return view[1]

    view_wrapper = zon_view(views)
    assert view_wrapper is not None, (
        'ZON view is not matching for ZON content')

    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/centerpage/zeitonline')
    request = mock.Mock()
    assert view_wrapper.__predicates__[0](context, request), (
        'The predicate does not work for ZON content')

    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/centerpage/index')
    assert view_wrapper.__predicates__[0](context, request) is False, (
        'The predicate should not work for ZMO Content')

    # TODO: has to be adapted (as)
    # context = zeit.cms.interfaces.ICMSContent(
    #     'http://xml.zeit.de/centerpage/zmo_zon_matching')
    # assert view_wrapper.__predicates__[0](context, request) is False, (
    #     'The predicate should not work for ZMO Content, even if '
    #     'rebrush_website_content is set to True.')


def test_custom_predicate_should_only_match_zmo_content(application):
    pviews = pyramid.scripts.pviews.PViewsCommand([])
    registry = application.zeit_app.config.registry
    views = pviews._find_view('/centerpage/index', registry).views

    # Just a helper, since the position in pviews in unpredictable
    def zmo_view(pviews):
        for view in pviews:
            if view[1].__dict__['__original_view__'] == (
                    zeit.web.magazin.view_centerpage.Centerpage):
                return view[1]

    view_wrapper = zmo_view(views)
    assert view_wrapper is not None, (
        'ZMO view is not matching for ZMO content')

    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/centerpage/index')
    request = mock.Mock()
    assert view_wrapper.__predicates__[0](context, request), (
        'The predicate does not work for ZMO content')

    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/centerpage/zeitonline')
    assert view_wrapper.__predicates__[0](context, request) is False, (
        'The predicate should not work for ZON Content')

    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/centerpage/zmo_zon_matching')
    assert view_wrapper.__predicates__[0](context, request) is False, (
        'The predicate should not work for ZMO Content, if '
        'rebrush_website_content is set to True.')


def test_content_should_be_rendered_with_render_with_header(application):
    pviews = pyramid.scripts.pviews.PViewsCommand([])
    registry = application.zeit_app.config.registry
    views = pviews._find_view(
        '/zeit-online/render-with-header', registry).views

    def render_with_view(pviews):
        for view in pviews:
            if view[1].__dict__['__original_view__'] == (
                    zeit.web.core.view.surrender):
                return view[1]

    view_wrapper = render_with_view(views)
    assert view_wrapper is not None, (
        'We do not have a render-with view')
