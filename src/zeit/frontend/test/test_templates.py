# -*- coding: utf-8 -*-
from mock import Mock
from re import match
import pyramid.config
import pytest
import zeit.frontend.application
import pyramid.threadlocal


@pytest.fixture(scope="module")
def jinja2_env(request):
    app = zeit.frontend.application.Application()
    app.config = pyramid.config.Configurator()
    return app.configure_jinja()


def test_macro_p_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('templates/macros/article_macro.tpl')
    html = 'Alles nicht so <em>wichtig</em>, oder?!'
    lines = tpl.module.paragraph(html).splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    markup = '<p class="is-constrained is-centered">'
    markup += 'Alles nicht so <em>wichtig</em>, oder?!</p>'
    assert markup == output


def test_macro_raw_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('templates/macros/article_macro.tpl')
    css_class = 'raw'
    markup = '<div class="%s">'\
        '<blink>ZEIT ONLINE</blink>'\
        '</div>' % css_class
    obj = {'xml': '<blink>ZEIT ONLINE</blink>'}
    lines = tpl.module.raw(obj).splitlines()
    output = ""
    for line in lines:
        output += line
        assert markup == output


def test_macro_subpage_chapter_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('templates/macros/article_macro.tpl')
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


def test_macro_footer_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('templates/macros/layout_macro.tpl')

    # assert normal markup
    markup = '<footer class="main-footer">'\
        '<div class="main-footer__box is-constrained is-centered">'\
        '<div class="main-footer__ZM">'\
        '<span class="main-footer__ZM__img icon-zm-logo--white"></span>'\
        '</div><div class="main-footer__links"><div><ul><li>VERLAG</li>'\
        '<li><a href="http://www.zeit-verlagsgruppe.de/anzeigen/">'\
        'Mediadaten</a></li><li><a href="'\
        'http://www.zeitverlag.de/presse/rechte-und-lizenzen">'\
        'Rechte &amp; Lizenzen</a></li>'\
        '</ul></div><div><ul><li>Bildrechte</li>'\
        '<li><a href="http://www.zeit.de/hilfe/datenschutz">'\
        'Datenschutz</a></li>'\
        '<li><a href="'\
        'http://www.iqm.de/Medien/Online/nutzungsbasierte_'\
        'onlinewerbung.html">Cookies</a></li>'\
        '<li><a href="http://www.zeit.de/administratives/'\
        'agb-kommentare-artikel">AGB</a></li>'\
        '<li><a href="http://www.zeit.de/impressum/index">Impressum</a></li>'\
        '<li><a href="http://www.zeit.de/hilfe/hilfe">Hilfe/ Kontakt</a></li>'\
        '</ul></div></div></div></footer>'

    lines = tpl.module.main_footer().splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    assert markup == output


def test_macro_breadcrumbs_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('templates/macros/layout_macro.tpl')
    obj = [('text', 'link')]

    markup = '<div class="breadcrumbs-wrap "><div class="breadcrumbs"' \
        ' id="js-breadcrumbs"><div class="breadcrumbs__list-wrap">' \
        '<div class="breadcrumbs__list">' \
        '<div class="breadcrumbs__list__item" itemscope="itemscope"' \
        ' itemtype="http://data-vocabulary.org/Breadcrumb">' \
        '<a href="link" itemprop="url"><span itemprop="title">text</span>' \
        '</a></div></div></div></div></div>'
    lines = tpl.module.breadcrumbs(obj, False).splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    assert markup == output


def test_macro_breadcrumbs_should_produce_markup_for_longform(jinja2_env):
    tpl = jinja2_env.get_template('templates/macros/layout_macro.tpl')
    obj = [('text', 'link')]

    markup = '<div class="breadcrumbs-wrap is-full-width"><div class="breadcrumbs"' \
        ' id="js-breadcrumbs"><div class="breadcrumbs__list-wrap">' \
        '<div class="breadcrumbs__list">' \
        '<div class="breadcrumbs__list__item" itemscope="itemscope"' \
        ' itemtype="http://data-vocabulary.org/Breadcrumb">' \
        '<a href="link" itemprop="url"><span itemprop="title">text</span>' \
        '</a></div></div></div></div></div>'
    lines = tpl.module.breadcrumbs(obj, True).splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    assert markup == output


def test_macro_subpage_index_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('templates/macros/article_macro.tpl')
    css_index = 'article__subpage-index'
    markup_standart = ('<div class="%s"><div class="article__subpage-index__'
                       'title">&uuml;bersicht</div>') % css_index

    fake_page = type('Dummy', (object,), {})
    fake_page.number = 1
    fake_page.teaser = 'Erster'

    # assert normal markup
    markup = (u'%s<div class="article__subpage-index__item"><span class="'
        'article__subpage-index__item__count">1 &mdash; </span><span class="'
        'article__subpage-index__item__title-wrap"><a href="#kapitel1" class'
        '="article__subpage-index__item__title">Erster</a></span></div></div>'
        ) % (markup_standart)
    lines = tpl.module.subpage_index(
        [fake_page], 'Title', 2, css_index, '').splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    assert markup == output

    # assert active markup
    css_active = 'article__subpage-active'
    markup_active = (u'%s<div class="article__subpage-index__item"><span '
        'class="article__subpage-index__item__count">1 &mdash; </span><span '
        'class="article__subpage-index__item__title-wrap"><span class="'
        'article__subpage-index__item__title %s">Erster</span></span></div>'
        '</div>') % (markup_standart, css_active)
    lines_active = tpl.module.subpage_index(
        [fake_page], 'Title', 1, css_index, css_active).splitlines()
    output_active = ""
    for line in lines_active:
        output_active += line.strip()
    assert markup_active == output_active

    # assert empty subtitle
    assert '' == tpl.module.subpage_index(['1'], '', 1)


def test_macro_subpage_head_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('templates/macros/article_macro.tpl')
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


def test_macro_source_date_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('templates/macros/article_macro.tpl')
    markup = '<span class="article__head__meta__source">' \
        'zon</span><span class="article__head__meta__date">01.01.2013' \
        '</span>'
    lines = tpl.module.source_date('01.01.2013', 'zon').splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    assert markup == output


def test_macro_intertitle_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('templates/macros/article_macro.tpl')
    lines = tpl.module.intertitle("xy").splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    m = '<h3 class="article__subheading is-constrained is-centered">xy</h3>'
    assert m == output


def test_macro_citation_should_produce_valid_markup(jinja2_env):
    tpl = jinja2_env.get_template('templates/macros/article_macro.tpl')

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
    tpl = jinja2_env.get_template('templates/macros/article_macro.tpl')

    # test normal
    ad = {'type': 'rectangle'}
    markup = '<div class="iqdplace" data-place="medrec_8"></div>'
    lines = tpl.module.advertising(ad).splitlines()
    assert markup == lines[0].strip()

    # test inactive
    ad_inactive = {'type': 'no'}
    assert '' == tpl.module.advertising(ad_inactive)


def test_image_should_produce_markup(jinja2_env, monkeypatch):
    tpl = jinja2_env.get_template('templates/macros/article_macro.tpl')

    obj = [{'layout': 'large', 'css': 'figure-full-width',
            'caption': 'test', 'copyright': 'test',
            'attr_alt': 'My alt content',
            'attr_title': 'My title content'},
           {'layout': 'zmo-xl-header',
            'css': 'figure-header',
            'caption': 'test', 'copyright': 'test',
            'attr_alt': 'My alt content',
            'attr_title': 'My title content'},
           {'layout': 'zmo-medium-left',
            'css': 'figure-horizontal',
            'caption': 'test', 'copyright': 'test',
            'attr_alt': 'My alt content',
            'attr_title': 'My title content'},
           {'layout': 'zmo-medium-right',
            'css': 'figure-horizontal--right',
            'caption': 'test', 'copyright': 'test',
            'attr_alt': 'My alt content',
            'attr_title': 'My title content'},
           {'layout': 'zmo-medium-center', 'css': 'figure '
            'is-constrained is-centered', 'caption': 'test',
            'copyright': 'test',
            'attr_alt': 'My alt content',
            'attr_title': 'My title content'},
           {'layout': 'zmo-small-right',
            'css': 'figure-stamp--right',
            'caption': 'test', 'copyright': 'test',
            'attr_alt': 'My alt content',
            'attr_title': 'My title content'},
           {'layout': 'zmo-small-left', 'css': 'figure-stamp',
            'caption': 'test', 'copyright': 'test',
            'attr_alt': 'My alt content',
            'attr_title': 'My title content'},
           {'layout': 'zmo-small-right', 'css': 'figure-stamp--right',
            'caption': 'test', 'copyright': 'test',
            'attr_alt': 'My alt content',
            'attr_title': 'My title content'},
           {'layout': 'zmo-large-center',
            'css': 'figure-full-width',
            'caption': 'test', 'copyright': 'test',
            'attr_alt': 'My alt content',
            'attr_title': 'My title content'},
           {'layout': 'zmo-small-left', 'align': False, 'css': 'figure-stamp',
            'caption': 'test', 'copyright': 'test',
            'attr_alt': 'My alt content',
            'attr_title': 'My title content'},
           {'layout': 'zmo-small-right', 'align': False,
            'css': 'figure-stamp--right',
            'caption': 'test', 'copyright': 'test',
            'attr_alt': 'My alt content',
            'attr_title': 'My title content'},
           ]

    class Image(object):

        uniqueId = '/img/artikel/01/01.jpg'

        def __init__(self, data):
            vars(self).update(data)

    def get_current_request():
        request = Mock()
        request.route_url.return_value = 'http://localhost/'
        return request

    monkeypatch.setattr(
        pyramid.threadlocal, 'get_current_request', get_current_request)

    for el in obj:
        print el['css']
        print el['layout']
        lines = tpl.module.image(Image(el)).splitlines()
        output = ""
        for line in lines:
            output += line.strip()
        markup = '<figure class="%s"><div class="scaled-image">' \
                 '<!--\[if gte IE 9\]> --><noscript data-ratio="">' \
                 '<!-- <!\[endif\]--><img alt="%s" title="%s" ' \
                 'class="figure__media" ' \
                 'src="/img/artikel/01/bitblt-\d+x\d+-[a-z0-9]+/01.jpg" ' \
                 'data-ratio=""><!--\[if gte IE 9\]> --></noscript>' \
                 '<!-- <!\[endif\]--></div><figcaption ' \
                 'class="figure__caption">test<span ' \
                 'class="figure__copyright">test</span>' \
                 '</figcaption></figure>' \
                 % (el['css'], el['attr_alt'], el['attr_title'])
        assert match(markup, output)


def test_macro_headerimage_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('templates/macros/article_macro.tpl')
    obj = Mock()
    obj.caption = 'test'
    obj.copyright = 'test'
    obj.src = 'test.gif'

    lines = tpl.module.headerimage(obj).splitlines()
    output = ""
    for line in lines:
        output += line.strip()

    start = '<div class="scaled-image is-pixelperfect">' \
            '<!--[if gte IE 9]> --><noscript><!-- <![endif]-->' \
            '<img class="article__main-image--longform" src="'

    end = '--></noscript><!-- <![endif]--></div>testtest'
    assert output.startswith(start)
    assert output.endswith(end)


def test_macro_meta_author_should_produce_html_if_author_exists(jinja2_env):
    tpl = jinja2_env.get_template('templates/macros/article_macro.tpl')
    test_class = 'test'
    authors = [{'prefix': 'Von', 'href': 'www.zeit.de',
            'name': 'Tom', 'location': ', Bern', 'suffix': 'und'},
           {'prefix': '', 'href': '',
            'name': 'Anna', 'location': '', 'suffix': ''}]
    markup = 'Von<a href="www.zeit.de" class="test">Tom</a>, Bern' \
             'und<span class="test">Anna</span>'
    lines = tpl.module.meta_author(authors, test_class).splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    assert markup.strip() == output


def test_macro_meta_author_shouldnt_produce_html_if_no_author(jinja2_env):
    tpl = jinja2_env.get_template('templates/macros/article_macro.tpl')
    authors = []
    lines = tpl.module.meta_author(authors).splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    assert '' == output


def test_macro_focussed_nextread_produce_valid_markup(jinja2_env):
    tpl = jinja2_env.get_template('templates/macros/article_macro.tpl')

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
    tpl = jinja2_env.get_template('templates/macros/article_macro.tpl')

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
    obj = [
        {'format': 'zmo-small-left',
         'id': 1,
         'fig': '<figure class="figure-stamp" data-video="1">'},
        {'format': 'zmo-small-right',
         'id': 1,
         'fig': '<figure class="figure-stamp--right" data-video="1">'},
        {'format': 'zmo-large-center',
         'id': 1,
         'fig': '<figure class="figure-full-width" data-video="1">'},
        {'format': 'large',
         'id': 1,
         'fig': '<figure class="figure-full-width" data-video="1">'},
        {'format': 'zmo-small-left',
         'id': 1,
         'fig': '<figure class="figure-stamp" data-video="1">'},
        {'format': 'small',
         'id': 1,
         'fig': '<figure class="figure-stamp" data-video="1">'}]

    for el in obj:
        lines = tpl.module.video(el).splitlines()
        output = ""
        for line in lines:
            output += line.strip()
        print lines
        assert el['fig'] in output


def test_macro_headervideo_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('templates/macros/article_macro.tpl')

    # assert default video
    obj = {'video_still': 'test.jpg', 'source': 'test.mp4', 'id': 1}
    wrapper = '<div data-backgroundvideo="1'
    video = '<video preload="auto" autoplay="true" ' \
            'loop="loop" muted="muted" volume="0"'
    source = '<source src="test.mp4'
    source_webm = 'http://opendata.zeit.de/zmo-videos/1.webm'
    img = '<img '
    fallback = '<img class="article__main-image--longform' \
        ' video--fallback" src="test.jpg'
    lines = tpl.module.headervideo(obj).splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    assert wrapper in output
    assert video in output
    assert source in output
    assert source_webm in output
    assert img in output
    assert fallback in output


def test_macro_sharing_meta_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('templates/macros/layout_macro.tpl')

    # test usual
    obj = {'title': 'title', 'subtitle': 'subtitle', 'sharing_img': 'true',
           'twitter_card_type': 'summary'}
    request = {'host': 'test.de', 'path_info': '/myurl'}
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
          '<meta property="og:url" content="test.de/myurl">']
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

    # test video still is set as sharing img
    obj = {'title': 'title', 'subtitle': 'subtitle',
           'sharing_img': {'video_still': 'true'},
           'twitter_card_type': 'summary_large_image'}
    twitter = ['<meta name="twitter:card" content="summary_large_image">']
    image = ['<meta property="og:image" content="',
             '<link itemprop="image" rel="image_src"',
             '<meta name="twitter:image" content="']
    lines = tpl.module.sharing_meta(obj, request).splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    print output
    for twitter_meta in twitter:
        assert twitter_meta in output
    for img in image:
        print img
        assert img in output


def test_macro_ga_tracking_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('templates/macros/layout_macro.tpl')
    elems = ["<script",
             "_gaq.push(['_setAccount'",
             "_gaq.push(['_setDomainName'",
             "_gaq.push (['_gat._anonymizeIp'",
             "_gaq.push(['_trackPageview'",
             "</script"]
    lines = tpl.module.ga_tracking().splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    for el in elems:
        assert el in output


def test_macro_cc_tracking_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('templates/macros/layout_macro.tpl')
    string = "lebensart/mode/article"
    elems = ['<script',
             'src="http://cc.zeit.de/cc.gif?banner-channel=' + string,
             "</script"]
    lines = tpl.module.cc_tracking(string).splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    for el in elems:
        assert el in output


def test_macro_meetrics_tracking_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('templates/macros/layout_macro.tpl')
    elems = ['<script',
             'src="http://scripts.zeit.de/js/rsa.js"',
             'loadMWA208571()',
             'mainMWA208571()',
             "</script"]
    lines = tpl.module.meetrics_tracking().splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    for el in elems:
        assert el in output


def test_macro_webtrekk_tracking_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('templates/macros/layout_macro.tpl')
    obj = {'ressort': 'lebensart',
           'sub_ressort': 'mode',
           'type': 'article',
           'tracking_type': 'Artikel',
           'author': {
               'name': 'Martin Mustermann'},
           'banner_channel': 'lebensart/mode/article',
           'text_length': 1000,
           'rankedTagsList': 'test;test'}
    request = {'path_info': '/test/test'}
    el_def = ['<script',
              'src="http://scripts.zeit.de/static/js/webtrekk/webtrekk_v3.js"',
              "</script",
              "wt.sendinfo();",
              "http://zeit01.webtrekk.net/" +
              "981949533494636/wt.pl?p=311,redaktion" +
              ".lebensart.mode..Artikel.online./test/test,0,0,0,0,0,0,0,0" +
              "&amp;cg1=Redaktion&amp;cg2=Artikel&amp;cg3=lebensart" +
              "&amp;cg4=Online&amp;cp1=Martin Mustermann" +
              "&amp;cp2=lebensart/mode/article&amp;cp3=1&amp;cp4=test;test" +
              "&amp;cp6=1000&amp;cp7=&amp;cp9=lebensart/mode/article"]
    el_cont = ['1: "Redaktion"',
               '2: "Artikel"',
               '3: "lebensart"',
               '4: "Online"']
    el_cust = ['1: "Martin Mustermann"',
               '2: "lebensart/mode/article"',
               '3: "1/1"',
               '4: "test;test"',
               '6: "1000"',
               '7: ""',
               '9: "lebensart/mode/article"']
    lines = tpl.module.webtrekk_tracking(obj, request).splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    for el in el_def:
        assert el in output
    for el in el_cont:
        assert el in output
    for el in el_cust:
        assert el in output


def test_macro_ivw_ver1_tracking_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('templates/macros/layout_macro.tpl')
    string = "lebensart/mode/article"
    elems = ['<script',
             'var Z_IVW_RESSORT = "' + string,
             'var IVW="http://zeitonl.ivwbox.de/cgi-bin/ivw/CP/' + string,
             'document.write("<img src=',
             '</script',
             '<img alt="" src="http://zeitonl.ivwbox.de/cgi-bin/ivw/CP/'
             + string]
    lines = tpl.module.ivw_ver1_tracking(string).splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    for el in elems:
        assert el in output


def test_macro_ivw_ver2_tracking_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template('templates/macros/layout_macro.tpl')
    obj = {'ressort': 'lebensart',
           'sub_ressort': 'mode'}
    request = {'path_info': '/test/test'}
    elems = ['<script',
             '"st" : ""',
             '"cp" : "lebensart/mode/bild-text"',
             '"sv" : "ke"',
             '"co" : "URL: /test/test"',
             'iom.c(iam_data,1);'
             '</script']
    lines = tpl.module.ivw_ver2_tracking(obj, request).splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    for el in elems:
        assert el in output


def test_macro_adplace_should_produce_markup(jinja2_env):
    # todo: after importing banner.xml to the system
    # make multiple tests from this
    # with all standard banner
    tpl = jinja2_env.get_template('templates/macros/layout_macro.tpl')
    banner = {'name': 'superbanner',
              'tile': '1',
              'sizes': ['728x90'],
              'dcopt': 'ist',
              'label': 'anzeige',
              'noscript_width_height': ('728', '90'),
              'diuqilon': True,
              'min_width': 768}
    num = '123456789'
    markup = 'document.write(\'<script src="http://ad.de.doubleclick.net/' \
             'adj/zeitonline/zolmz;dcopt=ist;tile=1;\' + n_pbt + \';' \
             'sz=728x90;kw=iqadtile1,zeitonline,zeitmz,\'+ iqd_TestKW ' \
             '+ window.diuqilon + \';ord=\' + IQD_varPack.ord + \'?" type="text' \
             '/javascript"><\/script>\');'
    lines = tpl.module.adplace(banner).splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    assert markup in output


def test_add_publish_date_generates_script(jinja2_env):
    tpl = jinja2_env.get_template('templates/macros/article_macro.tpl')

    obj = [{'lm': None,
            'pd': '1.Januar2014',
            'markup': ''},
           {'lm': '2.Januar2014',
            'pd': '1.Januar2014',
            'markup': '1.Januar2014'}]

    for el in obj:
        lines = tpl.module.add_publish_date(el['lm'], el['pd']).splitlines()
        output = ""
        for line in lines:
            output += line.strip()
        assert el['markup'] in output


def test_date_meta_should_produce_metatags(jinja2_env):
    tpl = jinja2_env.get_template('templates/macros/layout_macro.tpl')

    obj = [{'date_last_published_semantic': '',
            'date_first_released_meta': '1.1.2011',
            'markup': '<meta name="last-modified" content="1.1.2011"/>'},
           {'date_last_published_semantic': '1.2.2011',
            'date_first_released_meta': '1.1.2011',
            'markup': '<meta name="last-modified" content="1.2.2011"/>'}]

    for el in obj:
        lines = tpl.module.date_meta(el).splitlines()
        output = ""
        for line in lines:
            output += line.strip()
        assert el['markup'] in output


def test_no_block_macro_should_produce_basically_no_markup(jinja2_env):
    tpl = jinja2_env.get_template('templates/macros/article_macro.tpl')
    assert tpl.module.no_block('') == ''
