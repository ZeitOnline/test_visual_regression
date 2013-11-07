import pytest
import pyramid.config
import pyramid_jinja2
import zeit.frontend.application


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


def test_macro_p_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('../templates/block_elements.tpl')
    html = 'Alles nicht so <em>wichtig</em>, oder?!'
    lines = tpl.module.p(html, 'test').splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    markup = '<p class="test">Alles nicht so <em>wichtig</em>, oder?!</p>'
    assert markup == output


def test_macro_authorlink_should_produce_valid_markup(jinja2_env):
    tpl = jinja2_env.get_template('../templates/block_elements.tpl')
    data = {'name': 'abc'}
    markup = '<span class="article__meta__author">abc</span>'
    assert markup == tpl.module.authorlink(data).strip()
    markup = '<a href="xyz" class="article__meta__author meta-link">abc</a>'
    data = {'name': 'abc', 'href': 'xyz'}
    assert markup == tpl.module.authorlink(data).strip()
