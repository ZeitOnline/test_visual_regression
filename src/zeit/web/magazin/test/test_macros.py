# -*- coding: utf-8 -*-
import mock
import lxml.html

import zeit.cms.interfaces

import zeit.web.core.interfaces


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
    markup = '<div class="%s" id="kapitel1">1 &mdash; Title</div>' % css_class
    lines = tpl.module.subpage_head(1, 'Title', css_class).splitlines()
    output = ''
    for line in lines:
        output += line.strip()
    assert markup == output

    # assert empty subtitle
    assert '' == tpl.module.subpage_head(1, '', css_class)


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


def test_image_template_should_produce_figure_markup(
        tplbrowser, dummy_request):
    block = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/01').main_image_block
    image = zeit.web.core.interfaces.IFrontendBlock(block)
    browser = tplbrowser(
        'zeit.web.magazin:templates/inc/asset/image_article.tpl',
        block=image, request=dummy_request)
    assert browser.cssselect('figure.figure-full-width')
    assert browser.cssselect('img.figure__media')
    assert browser.cssselect('span.figure__copyright')
    assert browser.cssselect('a')[0].attrib['href'] == 'http://links.to'


def test_image_template_should_produce_copyright_caption(
        tplbrowser, dummy_request):
    block = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/01').main_image_block
    image = zeit.web.core.interfaces.IFrontendBlock(block)
    browser = tplbrowser(
        'zeit.web.magazin:templates/inc/asset/image_article.tpl',
        block=image, request=dummy_request)
    copyright = browser.cssselect('.figure__copyright a')[0]
    assert copyright.attrib['href'] == 'http://foo.com'
    assert copyright.text_content() == u'© Andreas Gebert/dpa'


def test_image_template_should_designate_correct_layouts(testbrowser):
    browser = testbrowser('/zeit-magazin/article/inline-imagegroup')
    header = browser.cssselect('.article__head__media-item')[0]
    assert header.attrib['data-ratio'] == '1.77858439201'  # variant=original
    stamp = browser.cssselect('figure.figure-stamp--right img')[0]
    assert stamp.attrib['data-ratio'] == '0.75'  # variant=portrait
    fullwidth = browser.cssselect('figure.is-centered img')[0]
    assert fullwidth.attrib['data-ratio'] == '1.77777777778'  # variant=wide


def test_image_template_should_hide_none(testbrowser):
    # XXX I'd much rather change a caption in the article, but trying
    # to checkout raises ConstrainedNotSatisfiedError: xl-header. :-(
    with mock.patch('zeit.web.core.block._inline_html') as inline:
        inline.return_value = ''
        browser = testbrowser('/feature/feature_longform')
        assert '<span class="figure__text">None</span>' not in browser.contents


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
    module = tpl.make_module({'view': mock.Mock()})
    lines = module.video(obj).splitlines()
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
        lines = module.video(el).splitlines()
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
    fallback = ('<img class="video--fallback " src="http://live0.zeit.de/'
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


def test_macro_headervideo_handles_video_id_correctly(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/article_macro.tpl')

    obj = mock.Mock()
    obj.id = None
    obj.uniqueId = None

    # assert empty template
    lines = tpl.module.headervideo(obj).splitlines()
    output = ''
    for line in lines:
        output += line.strip()
    assert output.strip() == ''

    # assert set id
    obj.id = 1

    html = lxml.html.fromstring(tpl.module.headervideo(obj))
    vid = html.cssselect('div[data-backgroundvideo="1"]')
    assert len(vid) == 1

    # assert set uniqueid
    obj = {'uniqueId': '/2'}

    html = lxml.html.fromstring(tpl.module.headervideo(obj))
    vid = html.cssselect('div[data-backgroundvideo="2"]')

    assert len(vid) == 1


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


# TODO: Move tests into appropriate file / Cleanup (#OPS-386)
