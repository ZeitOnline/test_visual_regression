import mock
import transaction

import zeit.cms.interfaces
import zeit.retresco.connection


def test_intextlink_data_is_cached_per_request(application):
    a1 = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    a2 = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/02')
    tms = zeit.retresco.connection.TMS('http://example.com')
    with mock.patch.object(tms, '_request') as request:
        request.return_value = {}
        tms.get_article_keywords(a1)
        assert request.call_count == 1
        tms.get_article_body(a1)
        assert request.call_count == 1
        tms.get_article_keywords(a2)
        assert request.call_count == 2
        tms.get_article_body(a2)
        assert request.call_count == 2

        transaction.abort()
        tms.get_article_body(a1)
        assert request.call_count == 3
