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
