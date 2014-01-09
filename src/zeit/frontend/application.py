from babel.dates import format_datetime
import grokcore.component.zcml
import logging
import martian
import pkg_resources
import pyramid.config
import pyramid_jinja2
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
        jinja.trim_blocks = True
        return jinja

    def configure_zca(self):
        log.debug('Configuring ZCA')
        self.configure_product_config()
        context = zope.configuration.config.ConfigurationMachine()
        zope.configuration.xmlconfig.registerCommonDirectives(context)
        zope.configuration.xmlconfig.include(context, package=zeit.frontend)
        # can't use <grok> directive since we can't configure excludes there
        martian.grok_dotted_name(
            'zeit.frontend',
            grokcore.component.zcml.the_module_grokker,
            exclude_filter=lambda name: name in set(self.DONT_GROK),
            config=context)
        context.execute_actions()

    @property
    def repository_path(self):
        if ('repository_path' not in self.settings.keys() or
                self.settings['repository_path'] == None):
            return pkg_resources.resource_filename( __name__, 'data')
        return self.settings['repository_path']

    def configure_product_config(self):
        # XXX make configurable, but see #36
        zope.app.appsetup.product.setProductConfiguration('zeit.cms', {
            'keyword-configuration': _product_url(
                'zeit.cms.tagging.tests', 'keywords_config.xml'),
            'source-badges': _product_url(
                'zeit.cms.asset', 'badges.xml'),
            'source-banners': _product_url(
                'zeit.cms.content', 'banners.xml'),
            'source-keyword': _product_url(
                'zeit.cms.content', 'zeit-ontologie-prism.xml'),
            'source-navigation': _product_url(
                'zeit.cms.content', 'navigation.xml'),
            'source-products': _product_url(
                'zeit.cms.content', 'products.xml'),
            'source-serie': _product_url(
                'zeit.cms.content', 'serie.xml'),
            'whitelist-url': _product_url(
                'zeit.cms.tagging.tests', 'whitelist.xml'),
        })

        zope.app.appsetup.product.setProductConfiguration('zeit.connector', {
            'repository-path': self.repository_path,
        })

        zope.app.appsetup.product.setProductConfiguration(
            'zeit.content.article', {
                'genre-url': _product_url(
                    'zeit.frontend', 'data/config/article-genres.xml'),
                'image-layout-source': _product_url(
                    'zeit.frontend',
                    'data/config/article-image-layouts.xml'),
                'video-layout-source': _product_url(
                    'zeit.frontend',
                    'data/config/article-video-layouts.xml'),
                'htmlblock-layout-source': _product_url(
                    'zeit.frontend',
                    'data/config/article-htmlblock-layouts.xml'),
            }
        )

        zope.app.appsetup.product.setProductConfiguration(
            'zeit.magazin', {
                'article-template-source': _product_url(
                    'zeit.frontend',
                    'data/config/article-templates.xml'),
                'article-related-layout-source': _product_url(
                    'zeit.frontend',
                    'data/config/article-related-layouts.xml'),
            }
        )

    @property
    def pipeline(self):
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


def _product_url(package, path):
    return 'file://' + pkg_resources.resource_filename(package, path)


def translate_url(obj):
    return obj.replace("xml.zeit.de", "www.zeit.de", 1)


def format_date(obj, type):
    if type == 'long':
        format = "dd. MMMM yyyy, H:mm 'Uhr'"
        return format_datetime(obj, format, locale="de_De")
