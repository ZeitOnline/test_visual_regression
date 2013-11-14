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


def test_macro_intertitle_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('../templates/block_elements.tpl')
    lines = tpl.module.intertitle("xy").splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    m = '<h3 class="article__subheading is-constrained is-centered">xy</h3>'
    assert m == output


def test_macro_meta_author_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('../templates/block_elements.tpl')
    data = {'name': "y", 'prefix': ' von ', 'suffix': ', '}
    markup = 'von <span class="article__meta__author">y</span>,'
    assert markup == tpl.module.meta_author(data).strip()
    data['href'] = 'x'
    markup = 'von <a href="x" class="article__meta__author meta-link">y</a>,'
    assert markup == tpl.module.meta_author(data).strip()


def test_macro_authorlink_should_produce_valid_markup(jinja2_env):
    tpl = jinja2_env.get_template('../templates/block_elements.tpl')
    data = {'name': 'abc'}
    markup = '<span class="article__meta__author">abc</span>'
    assert markup == tpl.module.authorlink(data).strip()
    markup = '<a href="xyz" class="article__meta__author meta-link">abc</a>'
    data = {'name': 'abc', 'href': 'xyz'}
    assert markup == tpl.module.authorlink(data).strip()


def test_macro_subpage_chapter_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('../templates/block_elements.tpl')
    css_class = 'article__subpage-chapter'

    # assert normal markup
    markup = '<div class="%s">' \
        '<span>Kapitel 1</span>' \
        '<span>&mdash; Title &mdash;</span>' \
        '<span></span></div>' % css_class
    lines = tpl.module.subpage_chapter(1, 'Title', css_class).splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    assert markup == output

    # assert empty subtitle
    assert '' == tpl.module.subpage_chapter(0, '', '')


def test_macro_subpage_index_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('../templates/block_elements.tpl')
    css_index = 'article__subpage-index'
    markup_standart = '<div class="%s">' % css_index

    # assert normal markup
    markup = '%s<span><a href="#kapitel1">1</a></span></div>' % markup_standart
    lines = tpl.module.subpage_index(
        ['1'], 'Title', 2, css_index, '').splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    assert markup == output

    # assert active markup
    css_active = 'article__subpage-active'
    markup_active = '%s<span class="%s">1</span></div>' \
        % (markup_standart, css_active)
    lines_active = tpl.module.subpage_index(
        ['1'], 'Title', 1, css_index, css_active).splitlines()
    output_active = ""
    for line in lines_active:
        output_active += line.strip()
    assert markup_active == output_active

    # assert empty subtitle
    assert '' == tpl.module.subpage_index(['1'], '', 1)


def test_macro_subpage_head_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('../templates/block_elements.tpl')
    css_class = 'article__subpage-head'

    # assert normal markup
    markup = '<div class="%s">' \
        '<a name="kapitel1"></a>1 &mdash; Title</div>' % css_class
    lines = tpl.module.subpage_head(1, 'Title', css_class).splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    assert markup == output

    # assert empty subtitle
    assert '' == tpl.module.subpage_head(1, '', css_class)
