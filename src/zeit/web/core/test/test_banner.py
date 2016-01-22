import zeit.web.core.banner


def test_banner_source_should_be_parsed(application):
    assert len(zeit.web.core.banner.BANNER_SOURCE) == 15
    place = list(zeit.web.core.banner.BANNER_SOURCE)[0]
    assert place.tile == 1
    assert place.sizes == ['728x90', '800x250']
    assert place.dcopt == 'ist'
    assert place.diuqilon is True

    place = list(zeit.web.core.banner.BANNER_SOURCE)[3]
    assert place.tile == 4
    assert place.sizes == ['300x250']
    assert place.dcopt is None
    assert place.diuqilon is False


def test_igd_mobile_ids_source_should_be_parsed(application):
    assert len(zeit.web.core.banner.IQD_MOBILE_IDS_SOURCE) == 4


def test_banner_id_mappings_source_should_be_parsed(application):
    assert len(
        zeit.web.core.banner.BANNER_ID_MAPPINGS_SOURCE) == 20
