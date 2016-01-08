import zeit.web.core.sources


def test_feature_toggle_source_should_be_parsed(application):
    assert zeit.web.core.sources.FEATURE_TOGGLE_SOURCE.find('article_lineage')
    assert not zeit.web.core.sources.FEATURE_TOGGLE_SOURCE.find('dummy')
    assert not zeit.web.core.sources.FEATURE_TOGGLE_SOURCE.find('nonexistent')
