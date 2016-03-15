# -*- coding: utf-8 -*-


def test_gallery_renders(testbrowser):
    select = testbrowser('/campus/gallery/gallery').cssselect
    assert len(select('.summary, .byline, .metadata')) == 3
