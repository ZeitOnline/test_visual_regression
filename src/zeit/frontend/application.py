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
    config.add_static_view(name='css', path='zeit.frontend:css/')
    config.add_static_view(name='js', path='zeit.frontend:js/')
    config.add_static_view(name='img', path='zeit.frontend:img/')
    config.add_static_view(name='fonts', path='zeit.frontend:fonts/')
    config.scan(package=zeit.frontend)
    return config.make_wsgi_app()
