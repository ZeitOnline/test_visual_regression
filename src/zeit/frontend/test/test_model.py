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

@pytest.fixture(scope="module")
def jinja2_env(request):
    config = pyramid.config.Configurator()
    config.include('pyramid_jinja2')
    utility = config.registry.getUtility(pyramid_jinja2.IJinja2Environment)
    utility.tests['elem'] = zeit.frontend.application.is_block
    utility.filters['format_date'] = zeit.frontend.application.format_date
    utility.filters['translate_url'] = zeit.frontend.application.translate_url
    utility.trim_blocks = True
    return utility

def test_macro_authorlink_should_produce_valid_markup(jinja2_env):
    tpl = jinja2_env.get_template('../templates/block_elements.tpl')
    markup = '<span class="article__meta__author">Nico</span>'
    assert markup == tpl.module.authorlink(('Nico','')).strip()

def test_block_type_should_deliver_type_og_block_element():
    pass
