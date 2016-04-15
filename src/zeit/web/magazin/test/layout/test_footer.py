# -*- coding: utf-8 -*-


def test_footer_exists(testbrowser):
    select = testbrowser('/artikel/01').cssselect
    assert select('footer.main-footer')


def test_footer_has_logo(testbrowser):
    select = testbrowser('/artikel/01').cssselect
    assert select('svg.svg-symbol.main-footer__logo')
