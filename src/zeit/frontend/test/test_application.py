from zeit.frontend import application
from zeit.frontend.test import test_model


def test_block_type_should_deliver_type_of_block_element():
    assert application.block_type(test_model._mock_p()) == 'para'
    assert application.block_type(test_model._mock_img()) == 'img'
    i = test_model._mock_intertitle()
    assert application.block_type(i) == 'intertitle'
    assert application.block_type(test_model._mock_citation()) == 'citation'
