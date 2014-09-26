# -*- coding: utf-8 -*-
import mock
import zeit.web.site.view_centerpage
import pyramid.testing

def test_area_main_should_filter_teasers():
    context = mock.MagicMock()

    def create_mocked_teaserblocks():
        tb_large = mock.MagicMock()
        tb_large.layout.id = 'zon-large'
        tb_large.__len__.return_value = 2
        tb_large.__iter__.return_value = iter(['article'])

        tb_small = mock.MagicMock()
        tb_small.layout.id = 'zon-small'
        tb_small.__len__.return_value = 2
        tb_small.__iter__.return_value = iter(['article'])

        tb_no_layout = mock.MagicMock()
        tb_no_layout.layout = None
        tb_no_layout.__len__.return_value = 2

        tb_no_layout_id = mock.MagicMock()
        tb_no_layout_id.layout.id = None
        tb_no_layout_id.__len__.return_value = 2

        tb_no_teaser_in_block = mock.MagicMock()
        tb_no_teaser_in_block.layout.id = 'zon-small'
        tb_no_teaser_in_block.__iter__.return_value = iter([])


        return [tb_large, tb_small, tb_no_layout, tb_no_layout_id,
            tb_no_teaser_in_block]

    context['lead'].values = create_mocked_teaserblocks

    request = mock.Mock()
    cp = zeit.web.site.view_centerpage.Centerpage(context, request)

    assert len(cp.area_main) == 2
    assert cp.area_main[0][0] == 'zon-large'
    assert cp.area_main[0][1] == 'article'
    assert cp.area_main[1][0] == 'zon-small'
    assert cp.area_main[0][1] == 'article'
