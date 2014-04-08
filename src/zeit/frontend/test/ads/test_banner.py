import pytest
from zeit.frontend.banner import Place


def test_place_should_be_serialized(testserver):
    place = Place(1, ['728x90'], True, label='')
    assert place.__dict__ == {'dcopt': 'ist', 'diuqilon': True,
        'label': '', 'min_width': 0, 'name': 'tile_1',
        'noscript_width_height': ['728', '90'], 'sizes': ['728x90'],
        'tile': 1}


def test_place_should_raise_on_index_error(testserver):
    with pytest.raises(IndexError):
        Place(1, '123x456', True, label='')
