import pyramid.config
import pyramid_jinja2
import pytest
import zeit.frontend.application
import zeit.frontend.block


@pytest.fixture(scope="module")
def jinja2_env(request):
    config = pyramid.config.Configurator()
    config.include('pyramid_jinja2')
    utility = config.registry.getUtility(pyramid_jinja2.IJinja2Environment)
    utility.tests['elem'] = zeit.frontend.block.is_block
    utility.filters['format_date'] = zeit.frontend.application.format_date
    utility.filters['translate_url'] = zeit.frontend.application.translate_url
    utility.trim_blocks = True
    return utility


def test_macro_p_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('../templates/block_elements.tpl')
    html = 'Alles nicht so <em>wichtig</em>, oder?!'
    lines = tpl.module.paragraph(html).splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    markup = '<p class="is-constrained is-centered">'
    markup += 'Alles nicht so <em>wichtig</em>, oder?!</p>'
    assert markup == output


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


def test_macro_breadcrumbs_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('../templates/block_elements.tpl')
    obj = [{'link': 'link', 'text': 'text'}]

    markup = '<div class="breadcrumbs-wrap "><div class="breadcrumbs" ' \
        'id="js-breadcrumbs"><div class="breadcrumbs__trigger" ' \
        'id="js-breadcrumbs__trigger" data-alternate="Schlie&szlig;en">' \
        'Wo bin ich?</div><div class="breadcrumbs__list">' \
        '<div class="breadcrumbs__list__item" itemprop="breadcrumb">' \
        '<a href="link">text</a></div></div></div></div>'
    lines = tpl.module.breadcrumbs(obj, False).splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    assert markup == output

def test_macro_breadcrumbs_should_produce_markup_for_longform(jinja2_env):
    tpl = jinja2_env.get_template('../templates/block_elements.tpl')
    obj = [{'link': 'link', 'text': 'text'}]

    markup = '<div class="breadcrumbs-wrap is-full-width"><div class="breadcrumbs" ' \
        'id="js-breadcrumbs"><div class="breadcrumbs__trigger" ' \
        'id="js-breadcrumbs__trigger" data-alternate="Schlie&szlig;en">' \
        'Wo bin ich?</div><div class="breadcrumbs__list">' \
        '<div class="breadcrumbs__list__item" itemprop="breadcrumb">' \
        '<a href="link">text</a></div></div></div></div>'
    lines = tpl.module.breadcrumbs(obj, True).splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    assert markup == output


def test_macro_subpage_index_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('../templates/block_elements.tpl')
    css_index = 'article__subpage-index'
    markup_standart = '<div class="%s">' % css_index

    fake_page = type('Dummy', (object,), {})
    fake_page.number = 1
    fake_page.teaser = 'Erster'

    # assert normal markup
    markup = '%s<span><a href="#kapitel1">1 -- Erster</a></span></div>' % (
        markup_standart)
    lines = tpl.module.subpage_index(
        [fake_page], 'Title', 2, css_index, '').splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    assert markup == output

    # assert active markup
    css_active = 'article__subpage-active'
    markup_active = '%s<span class="%s">1 -- Erster</span></div>' \
        % (markup_standart, css_active)
    lines_active = tpl.module.subpage_index(
        [fake_page], 'Title', 1, css_index, css_active).splitlines()
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


def test_macro_author_date_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('../templates/block_elements.tpl')
    markup = '<span class="article__meta__source">' \
        'Aus zon</span><span class="article__meta__date">01.01.2013' \
        '</span>'
    lines = tpl.module.author_date('01.01.2013', 'zon').splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    assert markup == output


def test_macro_intertitle_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('../templates/block_elements.tpl')
    lines = tpl.module.intertitle("xy").splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    m = '<h3 class="article__subheading is-constrained is-centered">xy</h3>'
    assert m == output


def test_macro_citation_should_produce_valid_markup(jinja2_env):
    tpl = jinja2_env.get_template('../templates/block_elements.tpl')

    # assert normal quote
    obj = {'layout': 'quote', 'attribution': 'Autor',
           'url': 'www.zeit.de', 'text': 'Text'}
    lines = tpl.module.citation(obj).splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    markup = '<blockquote class="quote"><span class="quote__text">' \
        'Text</span><span class="quote__author"><a href="www.zeit.de">' \
        'Autor</a></span></blockquote>'
    assert markup == output

    # assert wider quote
    obj = {'layout': 'wide', 'attribution': 'Autor',
           'url': 'www.zeit.de', 'text': 'Text'}
    lines = tpl.module.citation(obj).splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    markup = '<blockquote class="quote--wide"><span class="quote__text">' \
        'Text</span><span class="quote__author"><a href="www.zeit.de">' \
        'Autor</a></span></blockquote>'
    assert markup == output


def test_macro_advertising_should_produce_script(jinja2_env):
    tpl = jinja2_env.get_template('../templates/block_elements.tpl')

    # test normal
    ad = {'type': 'rectangle'}
    markup = '<script data-name="ad__rectangle">'
    lines = tpl.module.advertising(ad).splitlines()
    assert markup == lines[0].strip()

    # test inactive
    ad_inactive = {'type': 'no'}
    assert '' == tpl.module.advertising(ad_inactive)


def test_image_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('../templates/block_elements.tpl')

    obj = [{'layout': 'large', 'css': 'figure-full-width',
            'caption': 'test', 'copyright': 'test'},
           {'layout': 'zmo_header',
            'css': 'article__main-image figure-full-width',
            'caption': 'test', 'copyright': 'test'},
           {'layout': 'medium', 'align': 'left', 'css': 'figure-horizontal',
            'caption': 'test', 'copyright': 'test'},
           {'layout': 'medium', 'align': 'right',
            'css': 'figure-horizontal--right',
            'caption': 'test', 'copyright': 'test'},
           {'layout': 'medium', 'align': False, 'css': 'figure '
            'is-constrained is-centered', 'caption': 'test',
            'copyright': 'test'},
           {'layout': 'small', 'align': 'right',
            'css': 'figure-stamp--right',
            'caption': 'test', 'copyright': 'test'},
           {'layout': 'small', 'align': False, 'css': 'figure-stamp',
            'caption': 'test', 'copyright': 'test'}]

    for el in obj:
        print el['css']
        lines = tpl.module.image(el).splitlines()
        output = ""
        for line in lines:
            output += line.strip()
        markup = '<figure class="%s"><img class="figure__media"' \
            ' src="http://placehold.it/160x90"><figcaption' \
            ' class="figure__caption">testtest</figcaption></figure>' \
            % el['css']
        assert markup == output


def test_macro_head_image_longform_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('../templates/block_elements.tpl')
    obj = {'caption': 'test', 'copyright': 'test', 'src': 'test.gif'}
    lines = tpl.module.head_image_longform(obj).splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    markup = '<div class="article__main-image--longform"' \
        ' style="background-image: url(test.gif)";>testtest</div>'
    assert markup == output


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


def test_macro_video_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('../templates/block_elements.tpl')

    # assert default video
    obj = {'id': '1', 'video_still': 'pic.jpg',
           'description': 'test', 'format': ''}
    fig = '<figure class="figure is-constrained is-centered" data-video="1">'
    img = '<img class="figure__media" src="pic.jpg">'
    cap = '<figcaption class="figure__caption">test</figcaption>'
    lines = tpl.module.video(obj).splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    assert fig in output
    assert img in output
    assert cap in output

    #assert different formates
    obj['format'] = 'small'
    fig = '<figure class="figure-stamp" data-video="1">'
    lines = tpl.module.video(obj).splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    assert fig in output
    obj['format'] = 'small-right'
    fig = '<figure class="figure-stamp--right" data-video="1">'
    lines = tpl.module.video(obj).splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    assert fig in output
    obj['format'] = 'large'
    fig = '<figure class="figure-full-width" data-video="1">'
    lines = tpl.module.video(obj).splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    assert fig in output
