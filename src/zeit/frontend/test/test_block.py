from zeit.frontend import testing
from zeit.frontend.block import block_type


def test_block_type_should_deliver_type_of_block_element():
    assert block_type(testing.mock_p()) == 'para'
    assert block_type(testing.mock_img()) == 'img'
    i = testing.mock_intertitle()
    assert block_type(i) == 'intertitle'
    assert block_type(testing.mock_citation()) == 'citation'
