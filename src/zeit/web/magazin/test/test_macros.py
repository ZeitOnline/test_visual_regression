# -*- coding: utf-8 -*-
import mock
import lxml.html

import zeit.cms.interfaces

import zeit.web.core.interfaces


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


def test_image_template_should_produce_figure_markup(tplbrowser):
    block = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/artikel/01').main_image_block
    image = zeit.web.core.interfaces.IFrontendBlock(block)
    image.href = 'http://localhost/foo'
    browser = tplbrowser(
        'zeit.web.magazin:templates/inc/asset/image_article.tpl', obj=image)
    assert browser.cssselect('figure.figure-full-width')
    assert browser.cssselect('img.figure__media')
    assert browser.cssselect('span.figure__copyright')
    assert browser.cssselect('a')[0].attrib['href'] == 'http://localhost/foo'


def test_image_template_should_produce_copyright_caption(tplbrowser):
    block = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/artikel/01').main_image_block
    image = zeit.web.core.interfaces.IFrontendBlock(block)
    browser = tplbrowser(
        'zeit.web.magazin:templates/inc/asset/image_article.tpl', obj=image)
    copyright = browser.cssselect('.figure__copyright a')[0]
    assert copyright.attrib['href'] == 'http://foo.de'
    assert copyright.text.strip() == u'© Andreas Gebert/dpa'


def test_image_template_should_designate_correct_layouts(testbrowser):
    browser = testbrowser('/zeit-magazin/article/inline-imagegroup')
    header = browser.cssselect('figure.figure-header img')[0]
    assert header.attrib['data-variant'] == 'original'
    stamp = browser.cssselect('figure.figure-stamp--right img')[0]
    assert stamp.attrib['data-variant'] == 'portrait'
    fullwidth = browser.cssselect('figure.figure-full-width img')[0]
    assert fullwidth.attrib['data-variant'] == 'wide'


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

    start = ('<div class="scaled-image is-pixelperfect article__head-image">'
             '<!--[if gt IE 8]><!--><noscript')
    middle = ('><!--<![endif]-->'
              '<img alt="test" title="test" class=" figure__media" src="')
    end = '--></noscript><!--<![endif]--></div>testtest'

    assert output.startswith(start)
    assert middle in output
    assert output.endswith(end)


def test_image_macro_should_not_autoescape_markup(testbrowser):
    browser = testbrowser('/feature/feature_longform')
    text = browser.cssselect('.figure-stamp--right .figure__text')[0]
    assert u'Heckler & Koch' in text.text


def test_image_macro_should_hide_none(testbrowser):
    # XXX I'd much rather change a caption in the article, but trying
    # to checkout raises ConstrainedNotSatisfiedError: xl-header. :-(
    with mock.patch('zeit.web.core.block._inline_html') as inline:
        inline.return_value = ''
        browser = testbrowser('/feature/feature_longform')
        assert '<span class="figure__text">None</span>' not in browser.contents


def test_macro_meta_author_should_produce_html_if_author_exists(
        application, jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/article_macro.tpl')
    test_class = 'test'
    authors = [{'prefix': 'Von', 'href': 'www.zeit.de', 'name': 'Tom',
                'location': ', Bern', 'suffix': 'und'},
               {'prefix': '', 'href': '', 'name': 'Anna', 'location': '',
                'suffix': ''}]
    markup = ('Von<a href="www.zeit.de" class="test" itemprop="url"><span '
              'itemprop="name">Tom</span></a>, Bernund<span class="test">'
              '<span itemprop="name">Anna</span></span>')
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
    module = tpl.make_module({'request': mock.Mock()})
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


def test_macro_head_user_is_logged_in_true_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/layout_macro.tpl')

    request = mock.Mock()
    request.session.user.picture = None

    # no pic: fallback svg is shown
    lines = tpl.module.head_user_is_logged_in_true(request)
    doc = lxml.html.fromstring(lines)
    assert 'main-nav__avatar' in doc.cssselect('svg')[0].attrib['class']

    # pic
    request = mock.Mock()
    request.registry.settings.community_host = 'www.zeit.de'
    request.registry.settings.sso_activate = False
    request.session.user.picture = (
        'http://www.zeit.de/community-static/test.jpg')
    request.session.user.uid = 1
    request.url = 'test'

    lines = tpl.module.head_user_is_logged_in_true(request)
    doc = lxml.html.fromstring(lines).cssselect

    assert doc('span .main-nav__avatar')[0].attrib['style'] == (
        'background-image: url(http://www.zeit.de/community-static/test.jpg)')
    assert doc('a')[0].attrib['href'] == 'www.zeit.de/user/1'
    assert doc('a')[0].attrib['id'] == 'hp.zm.topnav.community.account'
    assert doc('a')[1].attrib['href'] == 'www.zeit.de/logout?destination=test'
    assert doc('a')[1].attrib['id'] == 'hp.zm.topnav.community.logout'

    request = mock.Mock()
    request.registry.settings.sso_url = 'sso.zeit.de'
    request.registry.settings.community_host = 'www.zeit.de'
    request.registry.settings.sso_activate = True
    request.session.user.uid = 1
    request.url = 'test_sso'

    lines = tpl.module.head_user_is_logged_in_true(request)
    doc = lxml.html.fromstring(lines).cssselect

    assert doc('a')[0].attrib['href'] == 'www.zeit.de/user/1'
    assert doc('a')[1].attrib['href'] == 'sso.zeit.de/abmelden?url=test_sso'


def test_macro_head_user_is_logged_in_false_should_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/layout_macro.tpl')

    request = mock.Mock()
    request.registry.settings.community_host = 'www.zeit.de'
    request.registry.settings.sso_url = 'sso.zeit.de'
    request.url = 'test'
    request.registry.settings.sso_activate = False

    html = tpl.module.head_user_is_logged_in_false(request)
    doc = lxml.html.fromstring(html)
    elem_a = doc.cssselect('a')[0]
    assert elem_a.attrib['href'] == "www.zeit.de/user/login?destination=test"

    request.registry.settings.sso_activate = True
    html = tpl.module.head_user_is_logged_in_false(request)
    doc = lxml.html.fromstring(html)
    elem_a = doc.cssselect('a')[0]
    assert elem_a.attrib['href'] == "sso.zeit.de/anmelden?url=test"


def test_macro_main_nav_should_produce_correct_state_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/layout_macro.tpl')

    request = mock.Mock()
    view = mock.Mock()

    # logged in
    request.user = {'ssoid': '12345'}
    markup = '<div class="main-nav__menu__content" id="js-main-nav-content">'
    logged = 'Account'
    module = tpl.make_module({'request': request, 'view': view})
    lines = module.main_nav('true', request).splitlines()
    output = ''
    for line in lines:
        output += line.strip()

    assert markup in output

    # logged out
    request.user = {}
    markup = '<div class="main-nav__menu__content" id="js-main-nav-content">'
    unlogged = 'Anmelden'
    module = tpl.make_module({'request': request, 'view': view})
    lines = module.main_nav('true', request).splitlines()
    output = ''
    for line in lines:
        output += line.strip()

    assert markup in output


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
    module = tpl.make_module({'request': mock.Mock()})
    snippet = lxml.html.fromstring(module.copyrights(copyrights))

    assert len(snippet.cssselect('li.copyrights__entry')) == 2, (
        'Two copyright entries should be contained in the list.')

    assert snippet.cssselect(
        'li.copyrights__entry:nth-child(1) .copyrights__label a'), (
            'The first entry should produce a link element.')

    assert not snippet.cssselect(
        'li.copyrights__entry:nth-child(2) .copyrights__label a'), (
            'The second entry should not produce a link element.')


def test_macro_include_cp_ad_produces_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/centerpage_macro.tpl')
    lines = tpl.module.include_cp_ad().splitlines()
    output = ''
    for line in lines:
        output += line.strip()
    assert '<div class="cp_button--ad">' in output


def test_macro_liveblog_produces_html(application, jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.magazin:templates/macros/article_macro.tpl')
    tpl_module = tpl.make_module({'view': mock.Mock()})
    liveblog = mock.Mock()
    liveblog.blog_id = '999'
    lines = tpl_module.liveblog(liveblog).splitlines()
    output = ''
    for line in lines:
        output += line.strip()
    assert ('<esi:include src="http://www.zeit.de/liveblog-backend/999.html" '
            'onerror="continue" />') in output
