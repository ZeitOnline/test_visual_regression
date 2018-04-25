# -*- coding: utf-8 -*-


def test_schemaless_webtrekk_content_id_on_hp_overlay(testbrowser):
    browser = testbrowser('/zeit-online/slenderized-index')

    elements = browser.cssselect('#overlay-wrapper [data-tracking]')

    assert elements

    for element in elements:
        tracking = element.get('data-tracking')
        assert tracking.endswith('|localhost/zeit-online/slenderized-index')
