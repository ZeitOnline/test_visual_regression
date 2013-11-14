from zeit.frontend import application
from zeit.frontend.test import test_model

def test_block_type_should_deliver_type_of_block_element():
    assert application.block_type(test_model.__mock_p()) == 'para'
    assert application.block_type(test_model.__mock_img()) == 'img'
    assert application.block_type(test_model.__mock_intertitle()) == 'intertitle'
    assert application.block_type(test_model.__mock_citation()) == 'citation'

