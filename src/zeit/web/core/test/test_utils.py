import lxml.objectify

import zeit.cms.content.interfaces

import zeit.web.core.utils


def test_data_solr_should_produce_usable_results(application):
    conn = zeit.web.core.utils.DataSolr()
    try:
        conn.update_raw(None)
    except Exception as err:
        raise AssertionError(err.message)

    assert len(conn.search(None, 3)) == 3
    assert 'uniqueId' in list(conn.search(None, 1))[0]
    assert 'date_last_published' in list(conn.search(None, 1))[0]


def test_exposing_proxy_should_return_dummy_for_unresolveable_uniqueId(
        application):
    proxy = zeit.web.core.utils.LazyProxy({
        'uniqueId': 'http://xml.zeit.de/nonexistent', 'type': 'article'})
    assert proxy.ressort is None
    # assert nothing raised:
    zeit.cms.content.interfaces.IXMLReferenceUpdater(proxy).update(
        lxml.objectify.XML('<foo/>'))
