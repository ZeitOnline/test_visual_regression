# -*- coding: utf-8 -*-
import re

import mock
import pyramid.threadlocal
import pyramid.config
import lxml


def test_macro_p_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/article_macro.tpl')
    html = 'Alles nicht so <em>wichtig</em>, oder?!'
    lines = tpl.module.paragraph(html).splitlines()
    output = ''
    for line in lines:
        output += line.strip()
    markup = '<p class="is-constrained is-centered">'
    markup += 'Alles nicht so <em>wichtig</em>, oder?!</p>'
    assert markup == output


def test_macro_raw_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/article_macro.tpl')
    css_class = 'raw'
    markup = ('<div class="%s">'
              '<blink>ZEIT ONLINE</blink>'
              '</div>' % css_class)
    obj = {'xml': '<blink>ZEIT ONLINE</blink>'}
    lines = tpl.module.raw(obj).splitlines()
    output = ''
    for line in lines:
        output += line
        assert markup == output


def test_macro_subpage_chapter_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/article_macro.tpl')
    css_class = 'article__subpage-chapter'

    # assert normal markup
    markup = ('<div class="%s">'
              '<span>Kapitel 1</span>'
              '<span>&mdash; Title &mdash;</span>'
              '<span></span></div>' % css_class)
    lines = tpl.module.subpage_chapter(1, 'Title', css_class).splitlines()
    output = ''
    for line in lines:
        output += line.strip()
    assert markup == output

    # assert empty subtitle
    assert '' == str(tpl.module.subpage_chapter(0, '', '')).strip()


def test_macro_breadcrumbs_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/layout_macro.tpl')
    obj = [('text', 'link')]

    markup = ('<div class="breadcrumbs">'
              '<div class="breadcrumbs__list is-constrained is-centered">'
              '<div class="breadcrumbs__list__item" itemscope="itemscope"'
              ' itemtype="http://data-vocabulary.org/Breadcrumb">'
              '<a href="link" itemprop="url"><span itemprop="title">text'
              '</span></a></div></div></div>')
    lines = tpl.module.breadcrumbs(obj).splitlines()
    output = ''
    for line in lines:
        output += line.strip()
    assert markup == output


def test_macro_portraitbox_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/article_macro.tpl')
    obj = {'name': 'name', 'text': 'text'}

    markup = ('<figure class="portraitbox figure-stamp">'
              '<div class="portraitbox-heading">name</div>'
              'text</figure>')
    lines = tpl.module.portraitbox(obj).splitlines()
    output = ''
    for line in lines:
        output += line.strip()
    assert markup == output


def test_macro_subpage_index_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/article_macro.tpl')
    css_index = 'article__subpage-index'
    markup_standard = ('<div class="%s figure-stamp">'
                       '<div class="article__subpage-index__title">'
                       '&uuml;bersicht</div><ol>') % css_index

    fake_page = type('Dummy', (object,), {})
    fake_page.number = 1
    fake_page.teaser = 'Erster'

    # assert normal markup
    markup = (
        u'%s<li class="article__subpage-index__item"><span class="'
        'article__subpage-index__item__count">1 &mdash; </span><span class="'
        'article__subpage-index__item__title-wrap"><a href="#kapitel1" class="'
        'article__subpage-index__item__title js-scroll">Erster</a></span>'
        '</li></ol></div>') % (markup_standard)
    lines = tpl.module.subpage_index(
        [fake_page], 'Title', 2, css_index, '').splitlines()
    output = ''
    for line in lines:
        output += line.strip()
    assert markup == output

    # assert active markup
    css_active = 'article__subpage-active'
    markup_active = (
        u'%s<li class="article__subpage-index__item"><span '
        'class="article__subpage-index__item__count">1 &mdash; </span><span '
        'class="article__subpage-index__item__title-wrap"><span class="'
        'article__subpage-index__item__title %s">Erster</span></span></li>'
        '</ol></div>') % (markup_standard, css_active)
    lines_active = tpl.module.subpage_index(
        [fake_page], 'Title', 1, css_index, css_active).splitlines()
    output_active = ""
    for line in lines_active:
        output_active += line.strip()
    assert markup_active == output_active

    # assert empty subtitle
    assert '' == tpl.module.subpage_index(['1'], '', 1)


def test_macro_subpage_head_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/article_macro.tpl')
    css_class = 'article__subpage-head'

    # assert normal markup
    markup = ('<div class="%s">'
              '<a name="kapitel1"></a>1 &mdash; Title</div>' % css_class)
    lines = tpl.module.subpage_head(1, 'Title', css_class).splitlines()
    output = ''
    for line in lines:
        output += line.strip()
    assert markup == output

    # assert empty subtitle
    assert '' == tpl.module.subpage_head(1, '', css_class)


def test_macro_source_date_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/article_macro.tpl')
    markup = ('<span class="article__head__meta__source">'
              'zon</span><span class="article__head__meta__date">01.01.2013'
              '</span>')
    lines = tpl.module.source_date('01.01.2013', 'zon').splitlines()
    output = ''
    for line in lines:
        output += line.strip()
    assert markup == output


def test_macro_intertitle_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/article_macro.tpl')
    lines = tpl.module.intertitle("xy").splitlines()
    output = ''
    for line in lines:
        output += line.strip()
    m = '<h2 class="article__subheading is-constrained is-centered">xy</h2>'
    assert m == output


def test_macro_citation_should_produce_valid_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/article_macro.tpl')

    # assert normal quote
    obj = {'layout': 'quote', 'attribution': 'Autor',
           'url': 'www.zeit.de', 'text': 'Text'}
    lines = tpl.module.citation(obj).splitlines()
    output = ''
    for line in lines:
        output += line.strip()
    markup = ('<blockquote class="quote"><span class="quote__text">'
              'Text</span><span class="quote__author"><a href="www.zeit.de">'
              'Autor</a></span></blockquote>')
    assert markup == output

    # assert wider quote
    obj = {'layout': 'wide', 'attribution': 'Autor',
           'url': 'www.zeit.de', 'text': 'Text'}
    lines = tpl.module.citation(obj).splitlines()
    output = ''
    for line in lines:
        output += line.strip()
    markup = ('<blockquote class="quote--wide"><span class="quote__text">'
              'Text</span><span class="quote__author"><a href="www.zeit.de">'
              'Autor</a></span></blockquote>')
    assert markup == output


def test_macro_advertising_should_produce_script(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/article_macro.tpl')

    # test normal
    ad = {'type': 'rectangle'}
    markup = '<div class="iqdplace" data-place="medrec_8"></div>'
    lines = tpl.module.advertising(ad).splitlines()
    assert markup == lines[0].strip()

    # test inactive
    ad_inactive = {'type': 'no'}
    assert '' == tpl.module.advertising(ad_inactive)


def test_image_should_produce_markup(jinja2_env, monkeypatch):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/article_macro.tpl')

    obj = [{'layout': 'large', 'css': 'figure-full-width',
            'caption': 'test', 'copyright': (('test', None, False),),
            'alt': 'My alt content',
            'title': 'My title content'},
           {'layout': 'zmo-xl-header',
            'css': 'figure-header',
            'caption': 'test', 'copyright': (('test', None, False),),
            'alt': 'My alt content',
            'title': 'My title content'},
           {'layout': 'zmo-medium-left',
            'css': 'figure-horizontal',
            'caption': 'test', 'copyright': (('test', None, False),),
            'alt': 'My alt content',
            'title': 'My title content'},
           {'layout': 'zmo-medium-right',
            'css': 'figure-horizontal--right',
            'caption': 'test', 'copyright': (('test', None, False),),
            'alt': 'My alt content',
            'title': 'My title content'},
           {'layout': 'zmo-medium-center', 'css': 'figure '
            'is-constrained is-centered', 'caption': 'test',
            'copyright': (('test', None, False),),
            'alt': 'My alt content',
            'title': 'My title content'},
           {'layout': 'zmo-small-right',
            'css': 'figure-stamp--right',
            'caption': 'test', 'copyright': (('test', None, False),),
            'alt': 'My alt content',
            'title': 'My title content'},
           {'layout': 'zmo-small-left', 'css': 'figure-stamp',
            'caption': 'test', 'copyright': (('test', None, False),),
            'alt': 'My alt content',
            'title': 'My title content'},
           {'layout': 'zmo-small-right', 'css': 'figure-stamp--right',
            'caption': 'test', 'copyright': (('test', None, False),),
            'alt': 'My alt content',
            'title': 'My title content'},
           {'layout': 'zmo-large-center',
            'css': 'figure-full-width',
            'caption': 'test', 'copyright': (('test', None, False),),
            'alt': 'My alt content',
            'title': 'My title content'},
           {'layout': 'zmo-small-left', 'align': False, 'css': 'figure-stamp',
            'caption': 'test', 'copyright': (('test', None, False),),
            'alt': 'My alt content',
            'title': 'My title content'},
           {'layout': 'zmo-small-right', 'align': False,
            'css': 'figure-stamp--right',
            'caption': 'test',
            'copyright': (('test', 'http://www.test.de', False),),
            'alt': 'My alt content',
            'title': 'My title content'},
           ]

    class Image(object):

        uniqueId = '/img/artikel/01/01.jpg'

        def __init__(self, data):
            vars(self).update(data)

    def get_current_request():
        request = mock.Mock()
        request.route_url.return_value = 'http://localhost/'
        return request

    monkeypatch.setattr(
        pyramid.threadlocal, 'get_current_request', get_current_request)

    for el in obj:
        lines = tpl.module.image(Image(el)).splitlines()
        output = ''
        for line in lines:
            output += line.strip()
        if el['copyright'][0][1]:
            cr = ('<a href="' + el['copyright'][0][1] +
                  '" target="_blank">' + el['copyright'][0][0] + '</a>')
        else:
            cr = el['copyright'][0][0]
        markup = ('<figure class="%s"><div class="scaled-image">'
                  '<!--\\[if gt IE 8\\]><!--><noscript'
                  ' data-src='
                  '"/img/artikel/01/bitblt-\\d+x\\d+-[a-z0-9]+/01.jpg">'
                  '<!--<!\\[endif\\]--><img alt="%s" title="%s" '
                  'class=" figure__media" '
                  'src="/img/artikel/01/bitblt-\\d+x\\d+-[a-z0-9]+/01.jpg" '
                  'data-ratio=""><!--\\[if gt IE 8\\]><!--></noscript>'
                  '<!--<!\\[endif\\]--></div><figcaption '
                  'class="figure__caption"><span '
                  'class="figure__caption__text">test</span><span '
                  'class="figure__copyright">%s</span>'
                  '</figcaption></figure>'
                  % (el['css'], el['alt'], el['title'], cr))

        assert re.match(markup, output)


def test_macro_headerimage_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/article_macro.tpl')
    obj = mock.Mock()
    obj.caption = 'test'
    obj.copyright = 'test'
    obj.src = 'test.gif'
    obj.ratio = 1
    obj.alt = "test"
    obj.title = "test"

    lines = tpl.module.headerimage(obj).splitlines()
    output = ''
    for line in lines:
        output += line.strip()

    start = ('<div class="scaled-image is-pixelperfect">'
             '<!--[if gt IE 8]><!--><noscript')
    middle = ('><!--<![endif]-->'
              '<img alt="test" title="test" class="article__main-image--'
              'longform figure__media" src="')
    end = '--></noscript><!--<![endif]--></div>testtest'

    assert output.startswith(start)
    assert middle in output
    assert output.endswith(end)


def test_macro_meta_author_should_produce_html_if_author_exists(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/article_macro.tpl')
    test_class = 'test'
    authors = [{'prefix': 'Von', 'href': 'www.zeit.de', 'name': 'Tom',
                'location': ', Bern', 'suffix': 'und'},
               {'prefix': '', 'href': '', 'name': 'Anna', 'location': '',
                'suffix': ''}]
    markup = ('Von<a href="www.zeit.de" class="test">Tom</a>, Bern'
              'und<span class="test">Anna</span>')
    lines = tpl.module.meta_author(authors, test_class).splitlines()
    output = ''
    for line in lines:
        output += line.strip()
    assert markup.strip() == output


def test_macro_meta_author_shouldnt_produce_html_if_no_author(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/article_macro.tpl')
    authors = []
    lines = tpl.module.meta_author(authors).splitlines()
    output = ''
    for line in lines:
        output += line.strip()
    assert '' == output


def test_macro_video_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/article_macro.tpl')

    # assert default video
    obj = {'id': '1', 'video_still': 'pic.jpg',
           'description': 'test', 'format': '', 'title': 'title'}
    fig = '<figure class="figure is-constrained is-centered" data-video="1">'
    img = ('<img class="figure__media" src="pic.jpg" alt="Video: title"'
           ' title="Video: title">')

    cap = '<figcaption class="figure__caption">test</figcaption>'
    lines = tpl.module.video(obj).splitlines()
    output = ''
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
        output = ''
        for line in lines:
            output += line.strip()
        assert el['fig'] in output


def test_macro_headervideo_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/article_macro.tpl')

    # assert default video
    obj = {'highest_rendition': 'test.mp4', 'id': 1}
    wrapper = '<div data-backgroundvideo="1'
    video = ('<video preload="auto" '
             'loop="loop" muted="muted" volume="0"')
    source = '<source src="test.mp4'
    source_webm = 'http://live0.zeit.de/multimedia/videos/1.webm'
    img = '<img '
    fallback = ('<img class="video--fallback'
                ' article__main-image--longform" src="http://live0.zeit.de/'
                'multimedia/videos/1.jpg')
    lines = tpl.module.headervideo(obj).splitlines()
    output = ''
    for line in lines:
        output += line.strip()
    assert wrapper in output
    assert video in output
    assert source in output
    assert source_webm in output
    assert img in output
    assert fallback in output


def test_macro_sharing_meta_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/layout_macro.tpl')

    # test usual
    obj = {'title': 'title', 'subtitle': 'subtitle', 'image_group': 'true',
           'twitter_card_type': 'summary_large_image'}
    request = {'host': 'test.de', 'path_info': '/myurl'}
    twitter = ['<meta name="twitter:card" content="summary_large_image">',
               '<meta name="twitter:site" content="@zeitonline">',
               '<meta name="twitter:creator" content="@ZEITmagazin">',
               '<meta name="twitter:title" content="title">',
               '<meta name="twitter:description" content="subtitle">']
    fb = ['<meta property="og:site_name" content="ZEITmagazin">',
          '<meta property="fb:admins" content="595098294">',
          '<meta property="og:type" content="article">',
          '<meta property="og:title" content="title">',
          '<meta property="og:description" content="subtitle">',
          '<meta property="og:url" content="http://test.de/myurl">']
    image = ['<meta property="og:image" content="',
             '<link itemprop="image" rel="image_src"',
             '<meta name="twitter:image:src" content="']
    lines = tpl.module.sharing_meta(obj, request).splitlines()
    output = ''
    for line in lines:
        output += line.strip()
    for fb_meta in fb:
        assert fb_meta in output
    for twitter_meta in twitter:
        assert twitter_meta in output
    for img in image:
        assert img in output


def test_add_publish_date_generates_script(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/article_macro.tpl')

    obj = [{'lm': None,
            'pd': '1.Januar2014',
            'markup': ''},
           {'lm': '2.Januar2014',
            'pd': '1.Januar2014',
            'markup': '1.Januar2014'}]

    for el in obj:
        lines = tpl.module.add_publish_date(el['lm'], el['pd']).splitlines()
        output = ''
        for line in lines:
            output += line.strip()
        assert el['markup'] in output


def test_date_meta_should_produce_metatags(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/layout_macro.tpl')

    obj = [{'date_last_published_semantic': '',
            'date_first_released_meta': '1.1.2011',
            'markup': '<meta name="last-modified" content="1.1.2011"/>'},
           {'date_last_published_semantic': '1.2.2011',
            'date_first_released_meta': '1.1.2011',
            'markup': '<meta name="last-modified" content="1.2.2011"/>'}]

    for el in obj:
        lines = tpl.module.date_meta(el).splitlines()
        output = ''
        for line in lines:
            output += line.strip()
        assert el['markup'] in output


def test_no_block_macro_should_produce_basically_no_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/article_macro.tpl')
    assert tpl.module.no_block('') == ''


def test_macro_insert_responsive_image_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/layout_macro.tpl')
    image = mock.Mock()
    image.alt = 'ALT'
    image.title = 'TITLE'
    image.src = 'SRC'

    lines = tpl.module.insert_responsive_image(image).splitlines()
    output = ''
    for line in lines:
        output += line.strip()

    assert '<!--[if gt IE 8]><!-->' in output
    assert '<img alt="ALT"' in output
    assert 'title="TITLE"' in output
    assert '<!--<![endif]-->' in output


def test_macro_insert_responsive_image_should_produce_alternative_markup(
        jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/layout_macro.tpl')
    image = mock.Mock()
    image.alt = 'ALT'
    image.title = 'TITLE'
    image.src = 'SRC'

    lines = tpl.module.insert_responsive_image(image, 'CLASS').splitlines()
    output = ''
    for line in lines:
        output += line.strip()

    assert 'class="CLASS figure__media' in output


def test_macro_insert_responsive_image_should_produce_linked_image(
        jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/layout_macro.tpl')
    image = mock.Mock()
    image.href = 'http://www.test.de'
    page_type = 'article'

    lines = tpl.module.insert_responsive_image(
        image, '', page_type).splitlines()
    output = ''
    for line in lines:
        output += line.strip()

    assert '<a href="http://www.test.de">' in output


def test_macro_teaser_text_block_should_produce_markup(jinja2_env):
    # teaser_text_block(teaser, block, shade, supertitle. subtitle, icon)
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/centerpage_macro.tpl')
    teaser = mock.Mock()
    teaser.teaserSupertitle = "SUPATITLE"
    teaser.teaserTitle = "TITLE"
    teaser.teaserText = "TEXT"
    teaser.uniqueId = "ID"

    lines = tpl.module.teaser_text_block(teaser).splitlines()
    output = ''
    for line in lines:
        output += line.strip()

    assert ('<header class="cp_leader__title__wrap '
            'cp_leader__title__wrap--none">') in output
    assert '<a href="ID"><h2>' in output
    assert '<div class="cp_leader__supertitle">SUPATITLE</div>' in output
    assert '<div class="cp_leader__title">TITLE</div>' in output
    assert '<span class="cp_leader__subtitle">TEXT</span>' in output


def test_macro_teaser_text_block_should_fallback_to_supertitle(jinja2_env):
    # teaser_text_block(teaser, block, shade, supertitle. subtitle, icon)
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/centerpage_macro.tpl')
    teaser = mock.Mock()
    teaser.teaserSupertitle = None
    teaser.supertitle = "FALLBACK"

    teaser.teaserTitle = "TITLE"
    teaser.uniqueId = "ID"

    lines = tpl.module.teaser_text_block(teaser).splitlines()
    output = ''
    for line in lines:
        output += line.strip()

    assert 'FALLBACK' in output


def test_macro_teaser_text_block_should_produce_alternative_markup(
        jinja2_env):
    # teaser_text_block(teaser, block, shade, supertitle. subtitle, icon)
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/centerpage_macro.tpl')
    teaser = mock.Mock()
    teaser.teaserTitle = "TITLE"
    teaser.uniqueId = "ID"

    lines = tpl.module.teaser_text_block(
        teaser, 'button', 'dark', 'false', 'false', 'true').splitlines()
    output = ''
    for line in lines:
        output += line.strip()

    assert ('<header class="cp_button__title__wrap '
            'cp_button__title__wrap--dark">') in output
    assert '<div class="cp_button__supertitle' not in output
    assert '<div class="cp_button__title">TITLE</div>' in output
    assert '<div class="cp_button__subtitle' not in output


def test_macro_comments_count_should_produce_correct_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/centerpage_macro.tpl')
    markup = ('<span class="cp_comment__count__wrap '
              'icon-comments-count">3</span>')
    lines = tpl.module.comments_count(3).splitlines()
    output = ''
    for line in lines:
        output += line.strip()

    assert markup in output


def test_macro_head_user_is_logged_in_true_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/layout_macro.tpl')

    request = mock.Mock()
    request.app_info.user.picture = None

    # no pic
    markup = '<span class="main-nav__community__icon icon-avatar-std"></span>'

    lines = tpl.module.head_user_is_logged_in_true(request).splitlines()
    output = ''
    for line in lines:
        output += line.strip()

    assert markup in output

    # pic
    request = mock.Mock()
    request.app_info.community_host = 'www.zeit.de/'
    request.app_info.user.picture = 'test.jpg'
    request.app_info.user.uid = 1
    request.app_info.community_paths.logout = 'logout'
    request.url = 'test'

    markup = ('<span class="main-nav__community__icon"'
              ' style="background-image: url(www.zeit.de/test.jpg)"></span>')
    account = ('<a href="www.zeit.de/user/1"'
               ' id="hp.zm.topnav.community.account">Account</a>')
    logout = ('<a href="www.zeit.de/logout?destination=test"'
              ' id="hp.zm.topnav.community.logout">Logout</a>')

    lines = tpl.module.head_user_is_logged_in_true(request).splitlines()
    output = ''
    for line in lines:
        output += line.strip()

    assert markup in output
    assert account in output
    assert logout in output


def test_macro_head_user_is_logged_in_false_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/layout_macro.tpl')

    request = mock.Mock()
    request.app_info.community_host = 'www.zeit.de/'
    request.app_info.community_paths.login = 'login'
    request.app_info.community_paths.register = 'register'
    request.url = 'test'

    markup = ('<a href="www.zeit.de/login?destination=test"'
              ' id="hp.zm.topnav.community.login">Anmelden</a>')

    lines = tpl.module.head_user_is_logged_in_false(request).splitlines()
    output = ''
    for line in lines:
        output += line.strip()

    assert markup in output


def test_macro_main_nav_should_produce_correct_state_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/layout_macro.tpl')

    request = mock.Mock()

    # logged in
    request.app_info.authenticated = 'true'
    markup = '<div class="main-nav__menu__content" id="js-main-nav-content">'
    logged = 'Account'
    lines = tpl.module.main_nav('true', request).splitlines()
    output = ''
    for line in lines:
        output += line.strip()

    assert markup in output
    assert logged in output

    # logged out
    request.app_info.authenticated = None
    markup = '<div class="main-nav__menu__content" id="js-main-nav-content">'
    unlogged = 'Anmelden'
    lines = tpl.module.main_nav('true', request).splitlines()
    output = ''
    for line in lines:
        output += line.strip()

    assert markup in output
    assert unlogged in output


def test_macro_copyrights(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/layout_macro.tpl')
    copyrights = [
        dict(
            image=('http://localhost:9090/exampleimages/'
                   'artikel/mode.jpg'),
            label='Lorem ipsum Cillum laborum cupidatat officia.',
            link='http://www.zeit.de'
        ),
        dict(
            image=('http://localhost:9090/exampleimages/'
                   'artikel/briefmarke.jpg'),
            label='Lorem ipsum Ut dolor quis pariatur occaecat.',
            link=None
        )
    ]
    snippet = lxml.html.fromstring(tpl.module.copyrights(copyrights))

    assert len(snippet.cssselect('li.copyrights__entry')) == 2, (
        'Two copyright entries should be contained in the list.')

    assert snippet.cssselect('li.copyrights__entry:nth-child(1) '
                             'span.copyrights__entry__label a'), (
        'The first entry should produce a link element.')

    assert not snippet.cssselect('li.copyrights__entry:nth-child(2) '
                                 'span.copyrights__entry__label a'), (
        'The second entry should not produce a link element.')


def test_macro_include_cp_ad_produces_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/centerpage_macro.tpl')
    lines = tpl.module.include_cp_ad().splitlines()
    output = ''
    for line in lines:
        output += line.strip()
    assert '<div class="cp_button--ad">' in output


def test_macro_liveblog_produces_html(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/article_macro.tpl')
    liveblog = mock.Mock()
    liveblog.blog_id = '999'
    lines = tpl.module.liveblog(liveblog).splitlines()
    output = ''
    for line in lines:
        output += line.strip()
    assert ('<esi:include src="http://www.zeit.de/liveblog-backend/999.html" '
            'onerror="continue"></esi:include>') in output
    assert '<esi:remove>' in output
    assert '<div data-type="esi-content"></div>' in output
    assert '</esi:remove>' in output
