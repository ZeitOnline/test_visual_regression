import mock
import requests
import requests_mock
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


def test_status_codes_should_be_measured_correctly(request):
    metrics = zeit.web.core.metrics.Metrics('test', 'localhost', 0)
    with mock.patch('zope.component.getUtility') as getUtility:
        getUtility.return_value = metrics
        r = Requester()
        with mock.patch('statsd.Counter.increment') as increment:
            with zeit.web.core.metrics.http('my_metric') as record:
                response = r.test_200()
                record(response)
            increment.assert_called_with(
                'testzeit.web.core.test.test_metrics.my_metric.status.200', 1)

            with zeit.web.core.metrics.http('my_metric') as record:
                response = r.test_404()
                record(response)
            increment.assert_called_with(
                'testzeit.web.core.test.test_metrics.my_metric.status.404', 1)

            with zeit.web.core.metrics.http('my_metric') as record:
                response = r.test_503()
                record(response)
            increment.assert_called_with(
                'testzeit.web.core.test.test_metrics.my_metric.status.503', 1)

            with zeit.web.core.metrics.http('my_metric') as record:
                try:
                    response = r.test_timeout()
                    record(response)
                except:
                    pass
            increment.assert_called_with(
                'testzeit.web.core.test.test_metrics.my_metric.status.599', 1)


@requests_mock.Mocker()
class Requester(object):
    def test_200(self, m):
        m.get('http://test.com', status_code=200)
        return requests.get('http://test.com')

    def test_404(self, m):
        m.get('http://test.com', status_code=404)
        return requests.get('http://test.com')

    def test_503(self, m):
        m.get('http://test.com', status_code=503)
        return requests.get('http://test.com')

    def test_timeout(self, m):
        m.get('http://test.com', exc=requests.exceptions.ConnectTimeout)
        return requests.get('http://test.com')
