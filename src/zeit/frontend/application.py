import zeit.frontend
import zeit.frontend.model
import zeit.frontend.navigation
import pyramid.config
import pyramid_jinja2

def factory(global_config, **settings):
    config = pyramid.config.Configurator(settings=settings,
                                         root_factory=zeit.frontend.model.get_root)
    config.include('pyramid_jinja2')
    utility = config.registry.getUtility(pyramid_jinja2.IJinja2Environment)
    utility.globals.update(zeit.frontend.navigation.get_sets())
    config.add_renderer('.html', pyramid_jinja2.renderer_factory)
    config.add_route('json', 'json/*traverse')
    config.scan(package=zeit.frontend)
    return config.make_wsgi_app()
