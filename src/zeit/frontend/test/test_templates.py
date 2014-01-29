from mock import Mock
from re import match
import pyramid.config
import pytest
import zeit.frontend.application


@pytest.fixture(scope="module")
def jinja2_env(request):
    app = zeit.frontend.application.Application()
    app.config = pyramid.config.Configurator()
    return app.configure_jinja()


def test_macro_p_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('templates/block_elements.tpl')
    html = 'Alles nicht so <em>wichtig</em>, oder?!'
    lines = tpl.module.paragraph(html).splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    markup = '<p class="is-constrained is-centered">'
    markup += 'Alles nicht so <em>wichtig</em>, oder?!</p>'
    assert markup == output


def test_macro_subpage_chapter_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('templates/block_elements.tpl')
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
    tpl = jinja2_env.get_template('templates/block_elements.tpl')
    obj = [('text', 'link')]

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
    tpl = jinja2_env.get_template('templates/block_elements.tpl')
    obj = [('text', 'link')]

    markup = '<div class="breadcrumbs-wrap is-full-width">' \
        '<div class="breadcrumbs" ' \
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
    tpl = jinja2_env.get_template('templates/block_elements.tpl')
    css_index = 'article__subpage-index'
    markup_standart = '<div class="%s">' % css_index

    fake_page = type('Dummy', (object,), {})
    fake_page.number = 1
    fake_page.teaser = 'Erster'

    # assert normal markup
    markup = u'%s<span><a href="#kapitel1">1 \u2014 ' \
        'Erster</a></span></div>' % (markup_standart)
    lines = tpl.module.subpage_index(
        [fake_page], 'Title', 2, css_index, '').splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    assert markup == output

    # assert active markup
    css_active = 'article__subpage-active'
    markup_active = u'%s<span class="%s">1 \u2014 Erster</span></div>' \
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
    tpl = jinja2_env.get_template('templates/block_elements.tpl')
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
    tpl = jinja2_env.get_template('templates/block_elements.tpl')
    markup = '<span class="article__meta__source">' \
        'Aus zon</span><span class="article__meta__date">01.01.2013' \
        '</span>'
    lines = tpl.module.author_date('01.01.2013', 'zon').splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    assert markup == output


def test_macro_intertitle_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('templates/block_elements.tpl')
    lines = tpl.module.intertitle("xy").splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    m = '<h3 class="article__subheading is-constrained is-centered">xy</h3>'
    assert m == output


def test_macro_citation_should_produce_valid_markup(jinja2_env):
    tpl = jinja2_env.get_template('templates/block_elements.tpl')

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
    tpl = jinja2_env.get_template('templates/block_elements.tpl')

    # test normal
    ad = {'type': 'rectangle'}
    markup = '<div class="iqdplace" data-place="medrec_8"></div>'
    lines = tpl.module.advertising(ad).splitlines()
    assert markup == lines[0].strip()

    # test inactive
    ad_inactive = {'type': 'no'}
    assert '' == tpl.module.advertising(ad_inactive)


def test_image_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('templates/block_elements.tpl')

    obj = [{'layout': 'large', 'css': 'figure-full-width',
            'caption': 'test', 'copyright': 'test',
            'attr_alt': 'My alt content',
            'attr_title': 'My title content'},
           {'layout': 'zmo-xl',
            'css': 'article__main-image figure-full-width',
            'caption': 'test', 'copyright': 'test',
						'attr_alt': 'My alt content',
						'attr_title': 'My title content'},
           {'layout': 'zmo-medium', 'align': 'left',
            'css': 'figure-horizontal',
            'caption': 'test', 'copyright': 'test',
						'attr_alt': 'My alt content',
						'attr_title': 'My title content'},
           {'layout': 'zmo-medium', 'align': 'right',
            'css': 'figure-horizontal--right',
            'caption': 'test', 'copyright': 'test',
						'attr_alt': 'My alt content',
						'attr_title': 'My title content'},
           {'layout': 'zmo-medium', 'align': False, 'css': 'figure '
            'is-constrained is-centered', 'caption': 'test',
            'copyright': 'test',
						'attr_alt': 'My alt content',
						'attr_title': 'My title content'},
           {'layout': 'small', 'align': 'right',
            'css': 'figure-stamp--right',
            'caption': 'test', 'copyright': 'test',
						'attr_alt': 'My alt content',
						'attr_title': 'My title content'},
           {'layout': 'small', 'align': False, 'css': 'figure-stamp',
            'caption': 'test', 'copyright': 'test',
						'attr_alt': 'My alt content',
						'attr_title': 'My title content'}]

    class Image(object):

        src = '/img/artikel/01/01.jpg'

        def __init__(self, data):
            vars(self).update(data)

    for el in obj:
        print el['css']
        lines = tpl.module.image(Image(el)).splitlines()
        output = ""
        for line in lines:
            output += line.strip()
        markup = '<figure class="%s"><div class="scaled-image"><noscript>' \
            '<img alt="%s" title="%s" class="figure__media"' \
            ' src="/img/artikel/01/bitblt-\d+x\d+-[a-z0-9]+/01.jpg" ' \
            'data-ratio=""></noscript></div><figcaption' \
            ' class="figure__caption">testtest</figcaption></figure>' \
            % (el['css'], el['attr_alt'], el['attr_title'])

def test_macro_headerimage_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('templates/block_elements.tpl')
    obj = Mock()
    obj.caption = 'test'
    obj.copyright = 'test'
    obj.src = 'test.gif'

    lines = tpl.module.headerimage(obj).splitlines()
    output = ""
    for line in lines:
        output += line.strip()

    start = '<div class="scaled-image is-pixelperfect">' \
        '<noscript><img class="article__main-image--longform" src="'

    end = '"></noscript></div>testtest'
    assert output.startswith(start)
    assert output.endswith(end)


def test_macro_meta_author_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('templates/block_elements.tpl')
    data = {'name': "y", 'prefix': ' von ', 'suffix': ', '}
    markup = 'von <span class="article__meta__author">y</span>,'
    assert markup == tpl.module.meta_author(data).strip()
    data['href'] = 'x'
    markup = 'von <a href="x" class="article__meta__author meta-link">y</a>,'
    assert markup == tpl.module.meta_author(data).strip()


def test_macro_authorlink_should_produce_valid_markup(jinja2_env):
    tpl = jinja2_env.get_template('templates/block_elements.tpl')
    data = {'name': 'abc'}
    markup = '<span class="article__meta__author">abc</span>'
    assert markup == tpl.module.authorlink(data).strip()
    markup = '<a href="xyz" class="article__meta__author meta-link">abc</a>'
    data = {'name': 'abc', 'href': 'xyz'}
    assert markup == tpl.module.authorlink(data).strip()


def test_macro_focussed_nextread_produce_valid_markup(jinja2_env):
    tpl = jinja2_env.get_template('templates/block_elements.tpl')

    article = Mock()
    article.supertitle = "SUPER"
    article.title = "TITLE"
    article.uniqueId = "LINK"
    article.copyright = "CP"

    nextread = {
        'image': {
            'uniqueId': "http://images.zeit.de/k-b/k-b-540x304.jpg",
            'caption': "BU",
        },
        'layout': "base",
        'article': article,
    }

    m = '<aside class="article__nextread nextread-base is-centered">'
    i = 'title="BU" alt="BU" src="http://images.zeit.de/k-b/k-b-540x304.jpg">'
    s = '<span class="article__nextread__supertitle">SUPER</span>'
    t = '<span class="article__nextread__title">TITLE</span>'
    l = '<a title="SUPER: TITLE" href="LINK">'
    assert m in tpl.module.focussed_nextread(nextread)
    assert i in tpl.module.focussed_nextread(nextread)
    assert s in tpl.module.focussed_nextread(nextread)
    assert t in tpl.module.focussed_nextread(nextread)
    assert l in tpl.module.focussed_nextread(nextread)

    nextread['layout'] = "maximal"
    m = '<aside class="article__nextread nextread-maximal is-centered">'
    bi = '<div class="article__nextread__body is-centered" style='
    assert m in tpl.module.focussed_nextread(nextread)
    assert bi in tpl.module.focussed_nextread(nextread)

    nextread['layout'] = "minimal"
    m = '<aside class="article__nextread nextread-minimal is-centered">'
    assert m in tpl.module.focussed_nextread(nextread)


def test_macro_video_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('templates/block_elements.tpl')

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

    # assert different formates
    obj['format'] = 'zmo-small'
    fig = '<figure class="figure-stamp" data-video="1">'
    lines = tpl.module.video(obj).splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    assert fig in output
    obj['format'] = 'zmo-small-right'
    fig = '<figure class="figure-stamp--right" data-video="1">'
    lines = tpl.module.video(obj).splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    assert fig in output
    obj['format'] = 'zmo-large'
    fig = '<figure class="figure-full-width" data-video="1">'
    lines = tpl.module.video(obj).splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    assert fig in output


def test_macro_headervideo_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('templates/block_elements.tpl')

    # assert default video
    obj = {'video_still': 'test.jpg', 'source': 'test.mp4'}
    wrapper = '<div data-backgroundvideo="'
    video = '<video preload="auto" autoplay="true" ' \
            'loop="loop" muted="muted" volume="0" poster="test.jpg'
    source = '<source src="test.mp4'
    img = '<img '
    fallback = '<div class="article__main-image--longform' \
        ' video--fallback" style="background-image:url(test.jpg'
    lines = tpl.module.headervideo(obj).splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    assert wrapper in output
    assert video in output
    assert source in output
    assert img in output
    assert fallback in output


def test_macro_sharing_meta_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('templates/block_elements.tpl')

    # assert default video
    obj = {'title': 'title', 'subtitle': 'subtitle', 'sharing_img': 'true'}
    request = {'url': 'test.de'}
    twitter = ['<meta name="twitter:card" content="summary">',
               '<meta name="twitter:site" content="@zeitonline">',
               '<meta name="twitter:creator" content="@zeitonline">',
               '<meta name="twitter:title" content="title">',
               '<meta name="twitter:description" content="subtitle">']
    fb = ['<meta property="og:site_name" content="ZEIT ONLINE">',
          '<meta property="fb:admins" content="595098294">',
          '<meta property="og:type" content="article">',
          '<meta property="og:title" content="title">',
          '"og:description" itemprop="description" content="subtitle">',
          '<meta property="og:url" content="test.de">']
    image = ['<meta property="og:image" class="scaled-image" content="',
             '<link itemprop="image" class="scaled-image" rel="image_src"',
             '<meta class="scaled-image" name="twitter:image" content="']
    lines = tpl.module.sharing_meta(obj, request).splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    for fb_meta in fb:
        assert fb_meta in output
    for twitter_meta in twitter:
        assert twitter_meta in output
    for img in image:
        assert img in output
