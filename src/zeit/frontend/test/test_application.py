from zeit.frontend import application
from zeit.frontend import testing

def test_block_type_should_deliver_type_of_block_element():
    assert application.block_type(testing.mock_p()) == 'para'
    assert application.block_type(testing.mock_img()) == 'img'
    i = testing.mock_intertitle()
    assert application.block_type(i) == 'intertitle'
    assert application.block_type(testing.mock_citation()) == 'citation'
