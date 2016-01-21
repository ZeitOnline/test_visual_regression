import zeit.web.core.sources


def test_feature_toggle_source_should_be_parsed(application):
    assert zeit.web.core.sources.FEATURE_TOGGLE_SOURCE.find('article_lineage')
    assert not zeit.web.core.sources.FEATURE_TOGGLE_SOURCE.find('dummy')
    assert not zeit.web.core.sources.FEATURE_TOGGLE_SOURCE.find('nonexistent')


def test_banner_source_should_be_parsed(application):
    assert len(zeit.web.core.sources.BANNER_SOURCE) == 15
    place = list(zeit.web.core.sources.BANNER_SOURCE)[0]
    assert place.tile == 1
    assert place.sizes == ['728x90', '800x250']
    assert place.dcopt == 'ist'
    assert place.diuqilon is True

    place = list(zeit.web.core.sources.BANNER_SOURCE)[3]
    assert place.tile == 4
    assert place.sizes == ['300x250']
    assert place.dcopt is None
    assert place.diuqilon is False


def test_igd_mobile_ids_source_should_be_parsed(application):
    assert len(zeit.web.core.sources.IQD_MOBILE_IDS_SOURCE) == 4


def test_banner_id_mappings_source_should_be_parsed(application):
    assert len(
        zeit.web.core.sources.BANNER_ID_MAPPINGS_SOURCE) == 20
