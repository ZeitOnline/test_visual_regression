import contextlib
import logging
import resource
import socket
import sys
import time

import mock
import pyramid.events
import statsd
import zope.component
import zope.interface

import zeit.web.core.interfaces


log = logging.getLogger(__name__)
memory_log = logging.getLogger('memory')


class Metrics(object):

    zope.interface.implements(zeit.web.core.interfaces.IMetrics)

    def __init__(self, prefix, hostname, port):
        self.prefix = prefix
        self.statsd = statsd.Connection(hostname, port)

    def time(self, identifier):
        return self.timer().time(self.prefix + identifier)

    def increment(self, identifier, delta=1):
        self.counter().increment(self.prefix + identifier, delta)

    def set_gauge(self, identifier, value):
        self.gauge().send(self.prefix + identifier, value)

    def timer(self, identifier=None):
        if identifier is not None:
            identifier = self.prefix + identifier
        return statsd.Timer(identifier, self.statsd)

    def counter(self, identifier=None):
        if identifier is not None:
            identifier = self.prefix + identifier
        return statsd.Counter(identifier, self.statsd)

    def gauge(self, identifier=None):
        if identifier is not None:
            identifier = self.prefix + identifier
        return statsd.Gauge(identifier, self.statsd)


@zope.interface.implementer(zeit.web.core.interfaces.IMetrics)
def from_settings():
    settings = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    if settings.get('statsd_address'):
        log.info('Initializing metrics collection to statsd at %s',
                 settings['statsd_address'])
        hostname = socket.gethostname()
        # Hostname might be the FQDN, which we don't want in the metric name.
        hostname = hostname.replace('.zeit.de', '')
        hostname = hostname.replace('.', '-')
        return Metrics(
            'friedbert.%s.' % hostname,
            *settings['statsd_address'].split(':'))
    else:
        log.info(
            'Not initializing metrics collection, no statsd_address setting')
        metrics = mock.Mock()
        metrics.time = mock_contextmanager
        return metrics


@contextlib.contextmanager
def mock_contextmanager(self, *args, **kw):
    yield


def timer(identifier):
    if not identifier.startswith('zeit.'):
        module = sys._getframe(1).f_globals['__name__']
        identifier = '%s.%s' % (module, identifier)
    metrics = zope.component.getUtility(zeit.web.core.interfaces.IMetrics)
    return metrics.time(identifier)


@pyramid.events.subscriber(pyramid.events.NewRequest)
def view_timer_start(event):
    event.request.view_timer_start = time.time()
    event.request.memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss


@pyramid.events.subscriber(pyramid.events.ContextFound)
def view_timer_traversal(event):
    request = event.request

    if request.matched_route:
        # Detect static_view, see pyramid.config.view.StaticURLInfo.add().
        if request.matched_route.name.startswith('__'):
            view_name = 'static'
        # Detect dynamic blacklist routes, see zeit.web.core.application.
        elif request.matched_route.name.startswith('blacklist_'):
            view_name = 'blacklist'
        else:
            view_name = request.matched_route.name
    else:
        # It might be interesting to do something like context-view_name,
        # however e.g. for 404s the context is the folder and the view_name
        # the name of the thing that was not found, which is rather unhelpful.
        view_name = request.context.__class__.__name__.lower()

    metrics = zope.component.getUtility(zeit.web.core.interfaces.IMetrics)
    timer = metrics.timer(
        'zeit.web.core.view.pyramid.{view}'.format(view=view_name))
    all_timer = metrics.timer('zeit.web.core.view.pyramid.all')
    # Since we can decide the timer name only now, after we have the context,
    # we have to re-implement timer.start() ourselves here.
    timer._last = timer._start = request.view_timer_start
    all_timer._last = all_timer._start = request.view_timer_start

    timer.intermediate('traversal')
    all_timer.intermediate('traversal')

    request.view_timer = timer
    request.view_timer_all = all_timer


@pyramid.events.subscriber(pyramid.events.NewResponse)
def view_timer_rendering(event):
    if getattr(event.request, 'view_timer', None):
        event.request.view_timer.intermediate('rendering')
        event.request.view_timer.stop('total')
        event.request.view_timer_all.intermediate('rendering')
        event.request.view_timer_all.stop('total')
    if getattr(event.request, 'memory', None):
        memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        memory_delta = memory - event.request.memory
        memory_log.debug(
            'Memory delta %s: %s KB', event.request.path, memory_delta)
