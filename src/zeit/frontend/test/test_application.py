import pyramid.interfaces
import pyramid.testing
import zeit.frontend.application


def test_asset_url_includes_configured_prefix(app_settings):
    app_settings['asset_prefix'] = '/assets'
    app = zeit.frontend.application.Application()
    app.settings = app_settings
    config = app.configure_pyramid()
    config.commit()

    request = pyramid.testing.DummyRequest()
    # XXX pyramid doesn't make it really easy to test request methods
    request.registry = config.registry
    request._set_extensions(config.registry.getUtility(
        pyramid.interfaces.IRequestExtensions))

    assert (
        'http://example.com/assets/css/main.css' ==
        request.asset_url('css/main.css'))

    assert (
        'http://example.com/assets/' ==
        request.asset_url('/'))
