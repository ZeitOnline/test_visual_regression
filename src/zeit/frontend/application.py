from babel.dates import format_datetime
from grokcore.component import adapter, implementer
from repoze.bitblt.transform import compute_signature
from urlparse import urlsplit, urlunsplit
from zeit.frontend.article import ILongformArticle
from zeit.frontend.article import IShortformArticle
from zeit.frontend.centerpage import auto_select_asset
from zeit.frontend.centerpage import get_image_asset
from zeit.magazin.interfaces import IArticleTemplateSettings
import itertools
import jinja2
import logging
import os.path
import pkg_resources
import pyramid.config
import pyramid.threadlocal
import pyramid_jinja2
import re
import urlparse
import zeit.cms.interfaces
import zeit.connector
import zeit.frontend
import zeit.frontend.block
import zeit.frontend.navigation
import zope.app.appsetup.product
import zope.component
import zope.configuration.xmlconfig


log = logging.getLogger(__name__)


class Application(object):

    DONT_SCAN = ['.testing', '.test', '.preview']

    def __init__(self):
        self.settings = {}

    def __call__(self, global_config, **settings):
        self.settings.update(settings)
        self.configure()
        return self.make_wsgi_app(global_config)

    def configure(self):
        self.configure_zca()
        self.configure_pyramid()

    def configure_pyramid(self):
        registry = pyramid.registry.Registry(
            bases=(zope.component.getGlobalSiteManager(),))
        self.config = config = pyramid.config.Configurator(
            settings=self.settings,
            registry=registry)
        config.setup_registry(settings=self.settings)

        self.config.include('pyramid_tm')
        self.configure_jinja()
        self.config.include("cornice")

        log.debug('Configuring Pyramid')
        config.add_route('json', 'json/*traverse')
        config.add_route('comments', '/-comments/collection/*traverse')
        config.add_route('home', '/')
        config.add_route('health_check', '/health_check')
        config.add_static_view(name='css', path='zeit.frontend:css/')
        config.add_static_view(name='js', path='zeit.frontend:js/')
        config.add_static_view(name='img', path='zeit.frontend:img/')
        config.add_static_view(name='fonts', path='zeit.frontend:fonts/')

        #ToDo: Is this still needed. Can it be removed?
        config.add_static_view(name='mocks', path='zeit.frontend:dummy_html/')

        def asset_url(request, path, **kw):
            kw['_app_url'] = join_url_path(
                request.application_url, request.registry.settings.get(
                    'asset_prefix', ''))
            if path == '/':
                return request.route_url('home', **kw)
            if ':' not in path:
                path = 'zeit.frontend:' + path
            return request.static_url(path, **kw)
        config.add_request_method(asset_url)

        config.set_root_factory(self.get_repository)
        config.scan(package=zeit.frontend, ignore=self.DONT_SCAN)
        return config

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
        jinja.globals['get_teaser_template'] = most_sufficient_teaser_tpl
        jinja.globals['get_teaser_image'] = most_sufficient_teaser_img
        jinja.tests['elem'] = zeit.frontend.block.is_block
        jinja.filters['format_date'] = format_date
        jinja.filters['replace_list_seperator'] = replace_list_seperator
        jinja.filters['block_type'] = zeit.frontend.block.block_type
        jinja.filters['translate_url'] = translate_url
        jinja.filters['default_image_url'] = default_image_url
        jinja.filters['auto_select_asset'] = auto_select_asset
        jinja.filters['obj_debug'] = obj_debug
        jinja.filters['substring_from'] = substring_from
        jinja.filters['hide_none'] = hide_none
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
        self.configure_connector(context)
        context.execute_actions()

    def configure_connector(self, context):
        typ = self.settings['connector_type']
        allowed = ('dav', 'tbcdav', 'filesystem')
        if typ not in allowed:
            raise ValueError(
                'Invalid setting connector_type=%s, allowed are {%s}'
                % (typ, ', '.join(allowed)))
        zope.configuration.xmlconfig.include(
            context, package=zeit.connector, file='%s-connector.zcml' % typ)

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
            ('repoze.vhm', 'paste.filter_app_factory', 'vhm_xheaders', {}),
            ('remove_asset_prefix', 'factory', '', {})
        ]

    def remove_asset_prefix(self, app):
        return URLPrefixMiddleware(
            app, prefix=self.settings.get('asset_prefix', ''))

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


class URLPrefixMiddleware(object):
    """Removes a path prefix from the PATH_INFO if it is present.
    We use this so that if an ``asset_prefix`` is configured, we respond
    correctly for URLs both with and without the asset_prefix -- otherwise
    the reverse proxy in front of us would need to rewrite URLs with
    ``asset_prefix`` to strip it.
    """

    def __init__(self, app, prefix):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO']
        if path.startswith(self.prefix):
            environ['PATH_INFO'] = path.replace(self.prefix, '', 1)
        return self.app(environ, start_response)


def maybe_convert_egg_url(url):
    if not url.startswith('egg://'):
        return url
    parts = urlparse.urlparse(url)
    return 'file://' + pkg_resources.resource_filename(
        parts.netloc, parts.path[1:])


def join_url_path(base, path):
    parts = urlparse.urlsplit(base)
    path = os.path.join(parts.path, path)
    return urlparse.urlunsplit(
        (parts[0], parts[1], path, parts[3], parts[4]))


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


def obj_debug(value):
    try:
        res = []
        for k in dir(value):
            res.append('%r : %r;' % (k, getattr(value, k)))
        return '\n'.join(res)
    except AttributeError:
        return False


def substring_from(string, find):
    return string.split(find)[-1]


def hide_none(string):
    if string is None:
        return ''
    else:
        return string

def format_date(obj, type):
    format = ""
    if type == 'long':
        format = "dd. MMMM yyyy, H:mm 'Uhr'"
    elif type == 'short':
        format = "dd. MMMM yyyy"
    return format_datetime(obj, format, locale="de_De")


def replace_list_seperator(semicolonseperatedlist, seperator):
    return semicolonseperatedlist.replace(';', seperator)

# definition of default images sizes per layout context
default_images_sizes = {
    'default': (200, 300),
    'large': (800, 600),
    'small': (200, 300),
    '540x304': (200, 300),
}


def default_image_url(image,
                      image_pattern='default'):
    try:
        if hasattr(image, 'layout'):
            width, height = default_images_sizes.get(image.layout, (640, 480))
        else:
            width, height = default_images_sizes.get(image_pattern, (640, 480))
        # TODO: use secret from settings?
        signature = compute_signature(width, height, 'time')

        if image.uniqueId is None:
            return None

        scheme, netloc, path, query, fragment = urlsplit(image.uniqueId)
        parts = path.split('/')
        parts.insert(-1, 'bitblt-%sx%s-%s' % (width, height, signature))
        path = '/'.join(parts)
        url = urlunsplit((scheme, netloc, path, query, fragment))
        request = pyramid.threadlocal.get_current_request()
        return url.replace("http://xml.zeit.de/", request.route_url('home'), 1)
    except:
        log.debug('Cannot produce a default URL for %s', image)


def most_sufficient_teaser_tpl(block_layout,
                               content_type,
                               asset,
                               prefix='templates/inc/teaser/teaser_',
                               suffix='.html',
                               separator='_'):

    types = (block_layout, content_type, asset)
    defaults = ('default', 'default', 'default')
    zipped = zip(types, defaults)

    combinations = [t for t in itertools.product(*zipped)]
    func = lambda x: '%s%s%s' % (prefix, separator.join(x), suffix)
    return map(func, combinations)


def most_sufficient_teaser_img(teaser_block,
                               teaser,
                               asset_type=None,
                               file_type='jpg'):
    image_pattern = teaser_block.layout.image_pattern
    if asset_type is None:
        asset = auto_select_asset(teaser)
    elif asset_type == 'image':
        asset = get_image_asset(teaser)
    else:
        raise KeyError(asset_type)
    if not zeit.content.image.interfaces.IImageGroup.providedBy(asset):
        return None
    image_base_name = re.split('/', asset.uniqueId)[-1]
    image_id = '%s/%s-%s.%s' % \
        (asset.uniqueId, image_base_name, image_pattern, file_type)
    try:
        teaser_image = zeit.cms.interfaces.ICMSContent(image_id)
        image_url = default_image_url(
            teaser_image, image_pattern=image_pattern)
        return image_url
    except TypeError:
        return None


@adapter(zeit.cms.repository.interfaces.IRepository)
@implementer(pyramid.interfaces.ITraverser)
class RepositoryTraverser(pyramid.traversal.ResourceTreeTraverser):

    def __call__(self, request):
        try:
            tdict = super(RepositoryTraverser, self).__call__(request)
            context = tdict['context']
            if zeit.content.article.interfaces.IArticle.providedBy(context):
                if IArticleTemplateSettings(context).template == 'longform':
                    zope.interface.alsoProvides(context, ILongformArticle)
                if IArticleTemplateSettings(context).template == 'short':
                    zope.interface.alsoProvides(context, IShortformArticle)
            return self._change_viewname(tdict)
        except OSError, e:
            if e.errno == 2:
                raise pyramid.httpexceptions.HTTPNotFound()

    def _change_viewname(self, tdict):
        if tdict['view_name'][0:5] == 'seite' and not tdict['subpath']:
            tdict['view_name'] = 'seite'
        return tdict
