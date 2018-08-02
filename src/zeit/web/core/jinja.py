from __future__ import absolute_import

from jinja2._compat import string_types
import StringIO
import cProfile
import datetime
import email.utils
import functools
import inspect
import logging
import os
import pkg_resources
import pstats
import sys
import urlparse

import bugsnag
import jinja2.environment
import jinja2.exceptions
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


class Interrupt(BaseException):
    """Custom error class to deliberately escape fault-tolerant rendering."""

    pass


class Environment(jinja2.environment.Environment):
    """Custom jinja Environment class that uses our custom Undefined class as
    fallback for unknown filters, globals, tests, object-attributes and -items.
    This way, most flaws and faults in view classes can be caught and affected
    areas can be ommited from the rendered output.
    """

    def __init__(self, **kw):
        kw['undefined'] = Undefined
        super(Environment, self).__init__(**kw)
        self.filters = zeit.web.core.utils.defaultdict(Undefined, self.filters)
        self.globals = zeit.web.core.utils.defaultdict(Undefined, self.globals)
        self.tests = zeit.web.core.utils.defaultdict(Undefined, self.tests)
        self._wrap_in_safeguard(self.filters)
        self._wrap_in_safeguard(self.tests)

    def _wrap_in_safeguard(self, registry):
        """Wraps jinja built-in filters and tests in an exception-catching
        safeguard. User-defined filters/tests (@zeit.web.register_filter etc.)
        are added afterwards, therefore the decorators will wrap those.
        """
        for key, value in registry.items():
            registry[key] = wrap_in_safeguard(value)

    def handle_exception(
            self, exc_info=None, rendered=False, source_hint=None,
            send_http_error=True):
        if exc_info is None:
            exc_info = sys.exc_info()
        if issubclass(exc_info[0], pyramid.httpexceptions.HTTPException):
            raise exc_info[0], exc_info[1], exc_info[2]

        traceback = make_jinja_traceback(exc_info, source_hint)
        exc_info = traceback.exc_info

        try:
            request = pyramid.threadlocal.get_current_request()
            path = request.path_info.encode('ascii', 'backslashreplace')
        except Exception:
            request = None
            path = '<unknown>'
        log.error('Error while rendering %s', path, exc_info=exc_info)

        if send_http_error and request is not None:
            # Since we don't reraise the exception (as upstream does), we'll
            # still render *some* result, but in most cases that means a
            # totally blank page -- which definitely should not be cached.
            request.response.status = 500

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
            self.handle_exception(send_http_error=False)
            return self.undefined(obj=obj, name=name)

    def getitem(self, obj, argument):
        return self.__getsth__('getitem', obj, argument)

    def getattr(self, obj, attribute):
        return self.__getsth__('getattr', obj, attribute)


class Undefined(jinja2.runtime.Undefined):
    """Custom jinja Undefined class that represents unresolvable template
    statements and expressions. It ignores undefined errors, ensures it is
    printable and returns further Undefined objects if indexed or called.
    """

    def __html__(self):
        return jinja2.utils.Markup()

    @jinja2.utils.internalcode
    def _fail_with_undefined_error(self, *args, **kw):
        """Logs Undefined errors with traceback. Note that Jinja only calls
        this for "second-level" Undefined situations, i.e. when a template
        tries to access an attribute of an already Undefined object. This means
        ``{{ context.nonexistent }}`` is silent, but we'll be called for
        ``{{ context.nonexistent.thing }}``.
        """
        tb = make_jinja_traceback((
            self._undefined_exception,
            self._undefined_exception(self._error_message()),
            Traceback.from_current_stack()))
        log.warning(
            'Undefined while rendering %s', get_current_request_path(),
            exc_info=tb.exc_info)
        return self.__class__()

    def _error_message(self):
        from jinja2.utils import missing
        if zeit.cms.interfaces.ICMSContent.providedBy(self._undefined_obj):
            make_repr = cmscontent_repr
        else:
            make_repr = jinja2.utils.object_type_repr
        if self._undefined_hint is None:
            if self._undefined_obj is missing:
                hint = '%r is undefined' % self._undefined_name
            elif not isinstance(self._undefined_name, string_types):
                hint = '%s has no element %r' % (
                    make_repr(self._undefined_obj), self._undefined_name)
            else:
                hint = '%r has no attribute %r' % (
                    make_repr(self._undefined_obj), self._undefined_name)
        else:
            hint = self._undefined_hint
        return hint

    # The superclass assigns these method by copying the function, too,
    # so they don't pick up our overriden method by themselves unfortunately.
    __add__ = __radd__ = __mul__ = __rmul__ = __div__ = __rdiv__ = \
        __truediv__ = __rtruediv__ = __floordiv__ = __rfloordiv__ = \
        __mod__ = __rmod__ = __pos__ = __neg__ = __call__ = \
        __getitem__ = __lt__ = __le__ = __gt__ = __ge__ = __int__ = \
        __float__ = __complex__ = __pow__ = __rpow__ = __sub__ = \
        __rsub__ = __getattr__ = _fail_with_undefined_error


def cmscontent_repr(content):
    return unicode(content).encode('ascii', 'backslashreplace')


class Traceback(object):
    """Fakes just enough of the types.TracebackType API to satisfy
    jinja2.utils.make_traceback.

    Inspired by <https://stackoverflow.com/a/13210518>.
    """

    def __init__(self, tb_frame, tb_lineno, tb_next):
        self.tb_frame = tb_frame
        self.tb_lineno = tb_lineno
        self.tb_next = tb_next

    @classmethod
    def from_current_stack(cls):
        """Converts inspect.stack() into chained Traceback objects."""
        # Skip inner frames until Undefined._fail_with_undefined_error()
        stack = inspect.stack(0)[3:]
        tb = None
        inside_template = True
        for item in stack:
            tb = cls(item[0], item[2], tb)
            if not inside_template:
                break
            if not item[0].f_globals.get('__jinja_template__'):
                # make_jinja_traceback requires one last non-template frame.
                inside_template = False
        return tb


def get_current_request_path():
    try:
        request = pyramid.threadlocal.get_current_request()
        return request.path_info.encode('ascii', 'backslashreplace')
    except:
        return '<unknown>'


def make_jinja_traceback(exc_info, source_hint=None):
    global _make_traceback
    if _make_traceback is None:
        from jinja2.debug import make_traceback as _make_traceback
    return _make_traceback(exc_info, source_hint)

# The function to create jinja traceback objects.  This is dynamically
# imported when the first exception occurs, since it incurs some overhead.
_make_traceback = None


def finalize(expr):
    """Custom jinja finalizer function to implicitly hide `None` expressions"""
    if expr is None:
        return u''
    return expr


def wrap_in_safeguard(fn):
    @functools.wraps(fn)
    def safeguard(*args, **kw):
        """Try to execute jinja environment modifier code and
        intercept potential exceptions. If execution is intercepted,
        return a jinja.Undefined object.

        :internal:
        """
        try:
            return fn(*args, **kw)
        except Exception:
            path = get_current_request_path()
            exc_info = sys.exc_info()
            log.error(
                'Error in %s.%s while rendering %s',
                fn.__module__, fn.__name__, path,
                exc_info=exc_info)
            bugsnag.notify(exc_info[1], traceback=exc_info[2], context=path)

            return zeit.web.core.jinja.Undefined()
    # Unfortunately, functools.wraps() doesn't preserve argument defaults.
    if hasattr(fn, 'func_defaults'):
        safeguard.func_defaults = fn.func_defaults
    return safeguard


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

    {% require image = produce_image('large') %}
        <img src="{{ image.url }}" class="{{ layout }}">
    {% endrequire %}

    Equivalent to:

    {% set image = produce_image('large') %}
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
        return assignments + [jinja2.nodes.If(condition, body, [], [])]
