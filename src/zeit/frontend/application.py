from babel.dates import format_datetime
from repoze.bitblt.transform import compute_signature
from urlparse import urlsplit, urlunsplit
import grokcore.component.zcml
import jinja2
import logging
import martian
import pkg_resources
import pyramid.config
import pyramid.threadlocal
import pyramid_jinja2
import urlparse
import zeit.frontend
import zeit.frontend.block
import zeit.frontend.navigation
import zope.app.appsetup.product
import zope.component
import zope.configuration.xmlconfig


log = logging.getLogger(__name__)


class Application(object):

    DONT_GROK = (
        'conftest',
        'test',
        'testing',
    )

    def __init__(self):
        self.settings = {}

    def __call__(self, global_config, **settings):
        self.settings.update(settings)
        self.configure()
        return self.make_wsgi_app(global_config)

    def configure(self):
        self.configure_zca()

        registry = pyramid.registry.Registry(
            bases=(zope.component.getGlobalSiteManager(),))
        self.config = config = pyramid.config.Configurator(
            settings=self.settings,
            registry=registry)
        config.setup_registry(settings=self.settings)

        self.configure_jinja()

        log.debug('Configuring Pyramid')
        config.add_route('home', '/')
        config.add_route('json', 'json/*traverse')
        config.add_static_view(name='css', path='zeit.frontend:css/')
        config.add_static_view(name='js', path='zeit.frontend:js/')
        config.add_static_view(name='img', path='zeit.frontend:img/')
        config.add_static_view(name='fonts', path='zeit.frontend:fonts/')
        config.add_static_view(name='mocks', path='zeit.frontend:dummy_html/')

        config.set_root_factory(self.get_repository)
        config.scan(package=zeit.frontend, ignore=['.testing', '.test'])

    def get_repository(self, request):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

    def configure_jinja(self):
        """Sets up names and filters that will be available for all
        templates."""
        log.debug('Configuring Jinja')
        self.config.include('pyramid_jinja2')
        self.config.add_renderer('.html', pyramid_jinja2.renderer_factory)
        jinja = self.config.registry.getUtility(
            pyramid_jinja2.IJinja2Environment)
        jinja.globals.update(zeit.frontend.navigation.get_sets())
        jinja.tests['elem'] = zeit.frontend.block.is_block
        jinja.filters['format_date'] = format_date
        jinja.filters['block_type'] = zeit.frontend.block.block_type
        jinja.filters['translate_url'] = translate_url
        jinja.filters['default_image_url'] = default_image_url
        jinja.trim_blocks = True
        return jinja

    def configure_zca(self):
        """Sets up zope.component registrations by reading our
        configure.zcml file."""
        log.debug('Configuring ZCA')
        self.configure_product_config()
        context = zope.configuration.config.ConfigurationMachine()
        zope.configuration.xmlconfig.registerCommonDirectives(context)
        zope.configuration.xmlconfig.include(context, package=zeit.frontend)
        zope.configuration.xmlconfig.include(
            context, package=zeit.connector, file='%s-connector.zcml' %
            self.settings['connector_type'])

        # can't use <grok> directive since we can't configure excludes there
        martian.grok_dotted_name(
            'zeit.frontend',
            grokcore.component.zcml.the_module_grokker,
            exclude_filter=lambda name: name in set(self.DONT_GROK),
            config=context)
        context.execute_actions()

    def configure_product_config(self):
        """Sets values of Zope Product Config used by vivi for configuration,
        using settings from the WSGI ini file.

        Requires the following naming convention in the ini file:
            vivi_<PACKAGE>_<SETTING> = <VALUE>
        for example
            vivi_zeit.connector_repository-path = egg://zeit.frontend/data

        (XXX This is based on the assumption that vivi never uses an underscore
        in a SETTING name.)

        For convenience we resolve egg:// URLs using pkg_resources into file://
        URLs. This functionality should probably move to vivi, see VIV-288.

        """
        for key, value in self.settings.items():
            if not key.startswith('vivi_'):
                continue

            ignored, package, setting = key.split('_')
            if zope.app.appsetup.product.getProductConfiguration(
                    package) is None:
                zope.app.appsetup.product.setProductConfiguration(package, {})
            config = zope.app.appsetup.product.getProductConfiguration(package)
            value = maybe_convert_egg_url(value)
            # XXX Stopgap until FRIED-12, since MockConnector does not
            # understand file-URLs
            if key == 'vivi_zeit.connector_repository-path':
                value = value.replace('file://', '')
            config[setting] = value

    @property
    def pipeline(self):
        """Configuration of a WSGI pipeline.

        Our WSGI application is wrapped in each filter in turn,
        so the first entry in this list is closest to the application,
        and the last entry is closest to the WSGI server.

        Each entry is a tuple (spec, protocol, name, arguments).
        The default meaning is to load an entry point called ``name`` of type
        ``protocol`` from the package ``spec`` and load it, passing
        ``arguments`` as kw parameters (thus, arguments must be a dict).

        If ``protocol`` is 'factory', then instead of an entry point the method
        of this object with the name ``spec`` is called, passing ``arguments``
        as kw parameters.

        """
        return [
            # ('repoze.vhm', 'paste.filter_app_factory', 'vhm_xheaders', {}),
        ]

    def make_wsgi_app(self, global_config):
        app = self.config.make_wsgi_app()
        for spec, protocol, name, extra in self.pipeline:
            if protocol == 'factory':
                factory = getattr(self, spec)
                app = factory(app, **extra)
                continue
            entrypoint = pkg_resources.get_entry_info(spec, protocol, name)
            app = entrypoint.load()(app, global_config, **extra)
        return app

factory = Application()


def maybe_convert_egg_url(url):
    if not url.startswith('egg://'):
        return url
    parts = urlparse.urlparse(url)
    return 'file://' + pkg_resources.resource_filename(
        parts.netloc, parts.path[1:])


@jinja2.contextfilter
def translate_url(context, url):
    if url is None:
        return None
    # XXX Is it really not possible to get to the actual template variables
    # (like context, view, request) through the jinja2 context?!??
    request = pyramid.threadlocal.get_current_request()
    if request is None:  # XXX should only happen in tests
        return url
    return url.replace("http://xml.zeit.de/", request.route_url('home'), 1)


def format_date(obj, type):
    if type == 'long':
        format = "dd. MMMM yyyy, H:mm 'Uhr'"
        return format_datetime(obj, format, locale="de_De")


# definition of default images sizes per layout context
default_images_sizes = dict(
    large=(300, 200),
    small=(200, 300),
)


def default_image_url(image):
    width, height = default_images_sizes.get(image.layout, (160, 90))
    # TODO: use secret from settings?
    signature = compute_signature(width, height, 'time')
    scheme, netloc, path, query, fragment = urlsplit(image.src)
    parts = path.split('/')
    parts.insert(-1, 'bitblt-%sx%s-%s' % (width, height, signature))
    path = '/'.join(parts)
    return urlunsplit((scheme, netloc, path, query, fragment))
