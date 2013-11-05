import  pytest
from zeit.frontend.model import _inline_html
from lxml import etree

class TestModel():
    def test_inline_html_should_filter_to_valid_html(self):
        p = """
                <p>Text <a href='foo'> ba </a> und <em>Text</em>
                abc <invalid>invalid</invalid></p>
            """

        xml = etree.fromstring(p)
        xml_str = """Text  <a href="foo"> ba </a> und <em>Text</em>
                abc invalid
"""
        assert str(_inline_html(xml)) == xml_str
