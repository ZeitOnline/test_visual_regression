import contextlib
import logging
import resource
import socket
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
        return statsd.Timer(self.prefix + identifier, self.statsd)

    def counter(self, identifier=None):
        return statsd.Counter(self.prefix + identifier, self.statsd)

    def gauge(self, identifier=None):
        return statsd.Gauge(self.prefix + identifier, self.statsd)


@zope.interface.implementer(zeit.web.core.interfaces.IMetrics)
def from_settings():
    settings = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    if settings.get('statsd_address'):
        log.info('Initializing metrics collection to statsd at %s',
                 settings['statsd_address'])
        return Metrics(
            'friedbert.%s.' % socket.gethostname(),
            *settings['statsd_address'].split(':'))
    else:
        log.info(
            'Not initializing metrics collection, no statsd_address setting')

        @contextlib.contextmanager
        def mock_time(self, identifier=None):
            yield
        metrics = mock.Mock()
        metrics.time = mock_time
        return metrics


def timer(identifier):
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
        else:
            view_name = request.matched_route.name
    else:
        view_name = request.view_name or 'default'

    metrics = zope.component.getUtility(zeit.web.core.interfaces.IMetrics)
    timer = metrics.timer(
        'zeit.web.core.view.pyramid.{context}-{view}'.format(
            context=request.context.__class__.__name__.lower(),
            view=view_name))
    # Since we can decide the timer name only now, after we have the context,
    # we have to re-implement timer.start() ourselves here.
    timer._last = timer._start = request.view_timer_start

    request.view_timer = timer
    request.view_timer.intermediate('traversal')


@pyramid.events.subscriber(pyramid.events.NewResponse)
def view_timer_rendering(event):
    event.request.view_timer.intermediate('rendering')
    event.request.view_timer.stop('total')
    memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    memory_delta = memory - event.request.memory
    memory_log.debug(
        'Memory delta %s: %s KB', event.request.path, memory_delta)
