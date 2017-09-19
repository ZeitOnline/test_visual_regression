import mock

import zeit.web.core.metrics


def test_timer_still_measures_on_exception(request):
    metrics = zeit.web.core.metrics.Metrics('test', 'localhost', 0)
    with mock.patch('zope.component.getUtility') as getUtility:
        getUtility.return_value = metrics
        with mock.patch('statsd.timer.Timer.stop') as stop:
            try:
                with zeit.web.core.metrics.timer('test'):
                    raise RuntimeError('provoked')
            except RuntimeError:
                pass
            assert stop.called
