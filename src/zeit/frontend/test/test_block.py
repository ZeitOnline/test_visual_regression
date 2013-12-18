from zeit.frontend.block import _inline_html
import lxml.etree


def test_inline_html_should_filter_to_valid_html():
    p = """
           <p>Text <a href='foo' class='myclass' rel='nofollow' data-foo='bar' foo='ron'> ba </a> und <em>Text</em>
           abc <invalid>invalid</invalid> valid: <em>valid</em></p>
       """

    xml = lxml.etree.fromstring(p)
    xml_str = """Text <a href="foo" class="myclass" rel="nofollow" data-foo="bar"> ba </a> und <em>Text</em>
           abc invalid valid: <em>valid</em>
"""
    print _inline_html(xml)
    assert xml_str == str(_inline_html(xml))
