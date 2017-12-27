# -*- coding: utf-8 -*-


def test_zmo_teasers_have_series_label(testbrowser):
    browser = testbrowser('/zeit-magazin/centerpage/teasers-to-series')
    select = browser.cssselect
    assert len(select('.teaser-fullwidth__series-label')) == 1
    assert len(select('.teaser-square-large__series-label')) == 1
    assert len(select('.teaser-landscape-large')) == 1
    assert len(select('.teaser-landscape-large-photo__series-label')) == 1
    assert len(select('.teaser-landscape-small__series-label')) == 2
    assert len(select('.teaser-upright-large__series-label')) == 1
    assert len(select('.card__series-label')) == 3
    assert len(select('.teaser-upright__series-label')) == 1

    assert len(select('.teaser-mtb-square')) == 3
    assert len(select('.teaser-mtb-square__series-label')) == 0
