# -*- coding: utf-8 -*-
import zeit.web.core.sources


def test_feature_toggle_source_should_be_parsed(application):
    assert zeit.web.core.sources.FEATURE_TOGGLE_SOURCE.factory.find(
        'third_party_modules') is True
