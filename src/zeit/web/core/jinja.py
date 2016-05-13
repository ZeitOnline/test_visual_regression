from __future__ import absolute_import

import StringIO
import cProfile
import datetime
import email.utils
import logging
import os
import pkg_resources
import pstats
import sys
import urlparse

import bugsnag
import jinja2.environment
import jinja2.ext
import jinja2.loaders
import jinja2.nodes
import jinja2.runtime
import jinja2.utils
import pyramid.settings
import pyramid.threadlocal
import pytz
import requests
import zope.component

import zeit.web.core.interfaces
import zeit.web.core.utils


log = logging.getLogger(__name__)
p_log = logging.getLogger('profile')


# The function to create jinja traceback objects.  This is dynamically
# imported on the first exception in handle_exception().
_make_traceback = None


def finalize(expr):
    """Custom jinja finalizer function to implicitly hide `None` expressions"""
    if expr is None:
        return u''
    return expr


class Undefined(jinja2.runtime.Undefined):
    """Custom jinja Undefined class that represents unresolvable template
    statements and expressions. It ignores undefined errors, ensures it is
    printable and returns further Undefined objects if indexed or called.
    """

    def __html__(self):
        return jinja2.utils.Markup()

    @jinja2.utils.internalcode
    def _fail_with_undefined_error(self, *args, **kw):
        pass

    __getattr__ = __getitem__ = __call__ = lambda self, *args: self.__class__()


class Interrupt(BaseException):
    """Custom error class to deliberately escape fault-tolerant rendering."""

    pass


class Environment(jinja2.environment.Environment):
    """Custom jinja Environment class that uses our custom Undefined class as
    fallback for unknown filters, globals, tests, object-attributes and -items.
    This way, most flaws and faults in view classes can be caught and affected
    areas can be ommited from the rendered output.
    """

    def __init__(self, undefined=Undefined, **kw):
        super(Environment, self).__init__(undefined=undefined, **kw)
        self.filters = zeit.web.core.utils.defaultdict(undefined, self.filters)
        self.globals = zeit.web.core.utils.defaultdict(undefined, self.globals)
        self.tests = zeit.web.core.utils.defaultdict(undefined, self.tests)

    def handle_exception(
            self, exc_info=None, rendered=False, source_hint=None):
        if exc_info is None:
            exc_info = sys.exc_info()
        if issubclass(exc_info[0], pyramid.httpexceptions.HTTPException):
            raise exc_info[0], exc_info[1], exc_info[2]

        global _make_traceback
        if _make_traceback is None:
            from jinja2.debug import make_traceback as _make_traceback
        traceback = _make_traceback(exc_info, source_hint)
        exc_info = traceback.standard_exc_info

        path = '<unknown>'
        try:
            request = pyramid.threadlocal.get_current_request()
            path = request.path_info
        except:
            pass
        log.error('Error rendering %s', path, exc_info=exc_info)

        group_by = None
        if exc_info[0] is jinja2.exceptions.UndefinedError:
            # The default group_by is the source code location, but for
            # UndefinedError that's always jinja2.Environment.getattr, which
            # doesn't tell us anything useful.
            group_by = exc_info[1].args[0]
        bugsnag.notify(exc_info[1], traceback=exc_info[2], context=path,
                       grouping_hash=group_by)

        return getattr(self.undefined(), '__html__', lambda: '')()

    def __getsth__(self, func, obj, name):
        try:
            return getattr(super(Environment, self), func)(obj, name)
        except Exception:
            self.handle_exception()
            return self.undefined(obj=obj, name=name)

    def getitem(self, obj, argument):
        return self.__getsth__('getitem', obj, argument)

    def getattr(self, obj, attribute):
        return self.__getsth__('getattr', obj, attribute)


class HTTPLoader(jinja2.loaders.BaseLoader):

    def __init__(self, url):
        self.url = url
        if url and not self.url.endswith('/'):
            self.url += '/'

    def get_source(self, environment, template):
        if not self.url:
            # XXX: Why doesn't this throw an exception?
            return (
                'ERROR: load_template_from_dav_url not configured',
                template, lambda: True)

        if self.url.startswith('egg://'):  # For tests
            parts = urlparse.urlparse(self.url)
            return (
                pkg_resources.resource_string(
                    parts.netloc, parts.path[1:] + template).decode('utf-8'),
                template, lambda: False)

        url = self.url + template
        log.debug('Loading template %r from %s', template, url)
        response = requests.get(url)
        return response.text, url, CompareModifiedHeader(
            url, response.headers.get('Last-Modified'))


class CompareModifiedHeader(object):
    """Compares a stored timestamp against the current Last-Modified header."""

    def __init__(self, url, timestamp):
        self.url = url
        self.last_retrieved = self.parse_rfc822(timestamp)

    def __call__(self):
        """Conforms to jinja2 uptodate semantics: Returns True if the template
        was not modified."""
        # NOTE: *Every time* a template is rendered we trigger an HTTP request.
        # Do we need introduce a delay to only perform the request every X
        # minutes?
        response = requests.head(self.url)
        last_modified = self.parse_rfc822(
            response.headers.get('Last-Modified'))
        return last_modified <= self.last_retrieved

    @staticmethod
    def parse_rfc822(timestamp):
        # XXX Dear stdlib, are you serious? Unfortunately, not even arrow
        # deals with RFC822 timestamps. This solution is sponsored by
        # <https://stackoverflow.com/questions/1568856>.
        if timestamp:
            return datetime.datetime.fromtimestamp(
                email.utils.mktime_tz(email.utils.parsedate_tz(timestamp)),
                pytz.utc)


class PrefixLoader(jinja2.BaseLoader):
    """Tweaked version of jinja2.PrefixLoader that defaults to prefix None
    if the requested path contains no prefix delimiter.
    """

    def __init__(self, mapping, delimiter='/'):
        self.mapping = mapping
        self.delimiter = delimiter

    def get_source(self, environment, template):
        if self.delimiter not in template:
            loader = self.mapping[None]
            name = template
        else:
            try:
                prefix, name = template.split(self.delimiter, 1)
                loader = self.mapping[prefix]
            except (ValueError, KeyError):
                raise jinja2.TemplateNotFound(template)
        try:
            return loader.get_source(environment, name)
        except jinja2.TemplateNotFound:
            # re-raise the exception with the correct fileame here.
            # (the one that includes the prefix)
            raise jinja2.TemplateNotFound(template)


class ProfilerExtension(jinja2.ext.Extension):
    """Profiler extension to overlay the rendered HTML with colorcoded
    rectangles that display the rendertime in milliseconds.

    Usage:

    {% profile %}
        {{ very_expensive_function() }}
    {% endprofile %}
    """

    tags = set(['profile'])

    def __init__(self, env):
        super(ProfilerExtension, self).__init__(env)
        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        self.active = pyramid.settings.asbool(
            conf.get('jinja2.enable_profiler'))
        self.profiler = None

    def parse(self, parser):
        parser.stream.next_if('name:profile')
        start = parser.stream.current.lineno
        body = parser.parse_statements(['name:endprofile'], drop_needle=True)
        stop = parser.stream.current.lineno
        if self.active:
            body.insert(0, jinja2.nodes.CallBlock(
                self.call_method('engage', []), [], [], [], lineno=start))
            body.append(jinja2.nodes.CallBlock(
                self.call_method('disengage', []), [], [], [], lineno=stop))

        return body

    def engage(self, *args, **kw):
        self.profiler = cProfile.Profile()
        self.profiler.enable()
        return '<div class="__pro__" style="outline:3px dashed #{};">'.format(
            os.urandom(3).encode('hex'))

    def disengage(self, *args, **kw):
        self.profiler.disable()
        stream = StringIO.StringIO()
        stats = pstats.Stats(self.profiler, stream=stream)
        stats.print_stats('zeit.web', 20)
        p_log.debug(stream.getvalue())
        return '<b position:relative;float:right;>{:.0f}ms</b></div>'.format(
            stats.total_tt * 1000)


class RequireExtension(jinja2.ext.Extension):
    """Wrapper extension that introduces golang-style conditional blocks via
    the require tag. It allows to assign expressions to variables that need to
    evaluate to True for the block to be executed. Syntax is similar to `with`.

    Usage:

    {% require image = get_image('large') %}
        <img src="{{ image.url }}" class="{{ layout }}">
    {% endrequire %}

    Equivalent to:

    {% set image = get_image('large') %}
    {% if image %}
        <img src="{{ image.url }}" class="{{ layout }}">
    {% endif %}
    """

    # TODO: Allow more specific conditional expressions than just bool(x).

    tags = set(['require'])

    def parse(self, parser):
        assignments = []
        condition = jinja2.nodes.Const(True)
        while parser.stream.current.type != 'block_end':
            lineno = parser.stream.current.lineno
            if assignments:
                parser.stream.expect('comma')
            parser.stream.next_if('name:require')
            target = parser.parse_assign_target()
            parser.stream.expect('assign')
            expr = parser.parse_expression()
            name = jinja2.nodes.Name(target.name, 'load')
            condition = jinja2.nodes.And(condition, name)
            assign = jinja2.nodes.Assign(target, expr, lineno=lineno)
            assignments.append(assign)

        body = parser.parse_statements(('name:endrequire',), drop_needle=True)
        return assignments + [jinja2.nodes.If(condition, body, [])]
