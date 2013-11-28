import zeit.frontend
import zeit.frontend.model
import zeit.frontend.navigation
import pyramid.config
import pyramid_jinja2
import zope.interface
import zeit.frontend.interfaces
from babel.dates import format_datetime


def factory(global_config, **settings):

    root = zeit.frontend.model.get_root
    config = pyramid.config.Configurator(settings=settings,
                                         root_factory=root)
    config.include('pyramid_jinja2')
    utility = config.registry.getUtility(pyramid_jinja2.IJinja2Environment)
    utility = configure_jinja2(utility)
    config.add_renderer('.html', pyramid_jinja2.renderer_factory)
    config.add_route('json', 'json/*traverse')
    config.add_static_view(name='css', path='zeit.frontend:css/')
    config.add_static_view(name='js', path='zeit.frontend:js/')
    config.add_static_view(name='img', path='zeit.frontend:img/')
    config.add_static_view(name='fonts', path='zeit.frontend:fonts/')
    config.add_static_view(name='mocks', path='zeit.frontend:dummy_html/')
    config.scan(package=zeit.frontend, ignore=['.testing', '.test'])
    return config.make_wsgi_app()


def configure_jinja2(jinja2_env):
    jinja2_env.tests['elem'] = is_block
    jinja2_env.filters['format_date'] = format_date
    jinja2_env.filters['block_type'] = block_type
    jinja2_env.filters['translate_url'] = translate_url
    jinja2_env.filters['base2src'] = baseId_to_src
    jinja2_env.globals.update(zeit.frontend.navigation.get_sets())
    jinja2_env.trim_blocks = True
    return jinja2_env


def is_block(obj, b_type):
    interface = None
    if b_type == 'p':
        interface = zeit.frontend.interfaces.IPara
    if b_type == 'image':
        interface = zeit.frontend.interfaces.IImg
    if b_type == 'intertitle':
        interface = zeit.frontend.interfaces.IIntertitle
    if b_type == 'citation':
        interface = zeit.frontend.interfaces.ICitation
    if b_type == 'advertising':
        interface = zeit.frontend.interfaces.IAdvertising
    return interface in zope.interface.providedBy(obj)


def block_type(obj):
    return type(obj).__name__.lower()


def translate_url(obj):
    return obj.replace("xml.zeit.de", "www.zeit.de", 1)


def format_date(obj, type):
    if type == 'long':
        format = "dd. MMMM yyyy, H:mm 'Uhr'"
        return format_datetime(obj, format, locale="de_De")


def baseId_to_src(obj):
    path = obj.rpartition("/")
    return path
