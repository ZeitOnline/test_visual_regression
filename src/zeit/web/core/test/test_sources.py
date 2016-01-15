import zeit.web.core.sources


def test_feature_toggle_source_should_be_parsed(application):
    assert zeit.web.core.sources.FEATURE_TOGGLE_SOURCE.find('article_lineage')
    assert not zeit.web.core.sources.FEATURE_TOGGLE_SOURCE.find('dummy')
    assert not zeit.web.core.sources.FEATURE_TOGGLE_SOURCE.find('nonexistent')


def test_banner_source_should_be_parsed(application):
    assert len(zeit.web.core.sources.BANNER_SOURCE.banner_list) == 15
    place = zeit.web.core.sources.BANNER_SOURCE.banner_list[0]
    assert place.tile == 1
    assert place.sizes == ['728x90', '800x250']
    assert place.dcopt == 'ist'
    assert place.diuqilon is True

    place = zeit.web.core.sources.BANNER_SOURCE.banner_list[3]
    assert place.tile == 4
    assert place.sizes == ['300x250']
    assert place.dcopt is None
    assert place.diuqilon is False
