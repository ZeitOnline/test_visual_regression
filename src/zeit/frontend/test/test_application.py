from zeit.frontend import application
from zeit.frontend import testing


def test_block_type_should_deliver_type_of_block_element():
    assert application.block_type(testing.mock_p()) == 'para'
    assert application.block_type(testing.mock_img()) == 'img'
    i = testing.mock_intertitle()
    assert application.block_type(i) == 'intertitle'
    assert application.block_type(testing.mock_citation()) == 'citation'


def test_filter_baseId_to_src_returns_src():
    data = "http://xml.zeit.de/p/d/1/k-b/"
    src = "http://images.zeit.de/p/d/1/k-b/k-b-540x304.jpg"
    assert application.baseId_to_src(data) == src
