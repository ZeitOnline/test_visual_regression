from lxml import etree
from zeit.frontend.model import _inline_html
import  pytest
import pyramid.config
import pyramid_jinja2
import zeit.frontend.application

def test_inline_html_should_filter_to_valid_html():
   p = """
           <p>Text <a href='foo'> ba </a> und <em>Text</em>
           abc <invalid>invalid</invalid></p>
       """

   xml = etree.fromstring(p)
   xml_str = """Text  <a href="foo"> ba </a> und <em>Text</em>
           abc invalid
"""
   assert str(_inline_html(xml)) == xml_str
