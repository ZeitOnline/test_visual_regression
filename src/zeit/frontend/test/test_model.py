from lxml import etree
from zeit.frontend.model import _inline_html
import pytest
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


def test_publish_date_should_produce_localized_date():
    import iso8601
    from zeit.frontend import view
    from mock import Mock

    pd = iso8601.parse_date("2013-10-10T10:00+00:00")
    m = Mock()
    m.publish_date = pd
    base = view.Base(m, Mock())

    # expected offset 200
    assert str(base.publish_date) == '2013-10-10 12:00:00+02:00'

    pd = iso8601.parse_date("2013-11-11T10:00+00:00")
    m = Mock()
    m.publish_date = pd
    base = view.Base(m, Mock())

    # expected offset 100
    assert str(base.publish_date) == '2013-11-11 11:00:00+01:00'


def test_construct_focussed_next_returns_next_read():
    from zeit.frontend.model import get_root
    from zeit.frontend.model import Content
    from lxml import objectify
    ref = """
        <root>
            <head>
            <references>
                <reference type="intern" href="URL">
                    <supertitle>SUPER</supertitle>
                    <title>TITLE</title>
                    <texta>XXX</texta>
                    <description>DESCRIPTION</description>
                    <image align="left" title="" base-id="BASEID" type="jpg" />
                </reference>
            </references>
            </head>
        </root>
        """
    xml = objectify.fromstring(ref)
    directory = get_root("pfft")
    content = Content(directory.base_path + '/artikel/03')
    nextread = content._construct_focussed_nextread(xml)
    assert nextread['supertitle'] == "SUPER"
    assert nextread['title'] == "TITLE"
    assert nextread['image'] == "BASEID"
    assert nextread['layout'] == "base"
    ref = """
        <root>
            <head>
            <references>
                <reference layout="maximal" type="intern" href="URL">
                    <supertitle>SUPER</supertitle>
                    <title>TITLE</title>
                    <texta>XXX</texta>
                    <description>DESCRIPTION</description>
                    <image align="left" title="" base-id="BASEID" type="jpg" />
                </reference>
            </references>
            </head>
        </root>
        """
    xml = objectify.fromstring(ref)
    nextread = content._construct_focussed_nextread(xml)
    assert nextread['layout'] == "maximal"
    ref = """
        <root>
            <head>
            <references>
                <reference layout="minimal" type="intern" href="URL">
                    <supertitle>SUPER</supertitle>
                    <title>TITLE</title>
                    <texta>XXX</texta>
                    <description>DESCRIPTION</description>
                    <image align="left" title="" base-id="BASEID" type="jpg" />
                </reference>
            </references>
            </head>
        </root>
        """
    xml = objectify.fromstring(ref)
    nextread = content._construct_focussed_nextread(xml)
    assert nextread['layout'] == "minimal"
