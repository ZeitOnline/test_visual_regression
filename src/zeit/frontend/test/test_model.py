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



def __mock_p():
    from zeit.frontend.model import Para
    p = """
           <p>Text <a href='foo'> ba </a> und <em>Text</em>
           abc</p>
       """

    xml = etree.fromstring(p)
    return Para(xml)

def __mock_img():
    from zeit.frontend.model import Img
    p = """
           <image layout="" align="" src="">
                <bu>foo</bu><copyright>foo</copyright>
           </image>
       """

    xml = etree.fromstring(p)
    return Img(xml)

def test_metabox_should_be_inserted_before_first_paragraph():
    from zeit.frontend.model import Metabox
    from zeit.frontend import model

    content = [__mock_p(), __mock_img(), __mock_p()]
    content = model.__insert_metabox(content)

    assert type(content[0]) ==  type(Metabox())

    content = [__mock_img(), __mock_p()]
    content = model.__insert_metabox(content)

    assert type(content[1]) ==  type(Metabox())

def test_publish_date_should_produce_localized_date():
    import iso8601
    from zeit.frontend import view
    from mock import Mock

    pd = iso8601.parse_date("2013-10-10T10:00+00:00")
    m = Mock()
    m.publish_date = pd
    base = view.Base(m,Mock())

    #expected offset 200
    assert str(base.publish_date) == '2013-10-10 12:00:00+02:00'

    pd = iso8601.parse_date("2013-11-11T10:00+00:00")
    m = Mock()
    m.publish_date = pd
    base = view.Base(m,Mock())

    # expected offset 100
    assert str(base.publish_date) == '2013-11-11 11:00:00+01:00'







