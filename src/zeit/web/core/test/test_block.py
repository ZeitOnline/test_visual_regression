# -*- coding: utf-8 -*-
import copy

import dogpile.cache
import lxml.etree
import mock

import pyramid_dogpile_cache2
import pyramid.testing
import zope.interface.declarations

import zeit.cms.interfaces
import zeit.edit.interfaces

import zeit.web.core.article
import zeit.web.core.centerpage
import zeit.web.site.view_article


def test_inline_html_should_filter_to_valid_html():
    p = ('<p>Text <a href="foo" class="myclass" rel="nofollow" '
         'data-foo="bar"> ba </a> und <em>Text</em> abc invalid valid: '
         '<em>valid</em></p>')

    xml = lxml.etree.fromstring(p)
    xml_str = ('Text <a href="foo" class="myclass" rel="nofollow" '
               'data-foo="bar"> ba </a> und <em>Text</em> abc invalid valid: '
               '<em>valid</em>')

    assert xml_str == (
        str(zeit.web.core.block._inline_html(xml)).replace('\n', ''))


def test_inline_html_should_return_none_on_non_xml_input():
    assert zeit.web.core.block._inline_html('foo') is None
    assert zeit.web.core.block._inline_html(None) is None


def test_inline_html_should_consider_additional_elements():
    ul = ('<ul>'
          '<li>The path of the <b>righteous</b> man</li>'
          '<li>is beset <a href="#in">on all sides</a> by the iniquities</li>'
          '<li>of the selfish and the tyranny of <i>evil men</i>.</li>'
          '</ul>')
    add = ['li', 'b', 'i']
    xml = lxml.etree.fromstring(ul)
    out = ('<li>The path of the <b>righteous</b> man</li>'
           '<li>is beset <a href="#in">on all sides</a> by the iniquities</li>'
           '<li>of the selfish and the tyranny of <i>evil men</i>.</li>')

    assert out == str(zeit.web.core.block._inline_html(xml, add)).strip()


def test_inline_html_should_not_render_empty_tags():
    assert str(zeit.web.core.block._inline_html(lxml.etree.fromstring(
        '<em></em>'))).strip() == '<em></em>'


def test_video_block_should_be_fault_tolerant_if_video_is_none(application):
    model_block = mock.Mock()
    model_block.layout = 'zmo-medium-center'
    model_block.video = None
    video = zeit.web.core.block.Video(model_block)
    assert not hasattr(video, 'video_still')

    model_block = mock.Mock()
    model_block.layout = 'zmo-medium-center'
    model_block.video = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/video/3537342483001')
    video = zeit.web.core.block.Video(model_block)
    assert hasattr(video, 'video_still')


def test_image_should_render_supertitle_and_caption_in_alt_tag(monkeypatch):
    context = mock.Mock()
    context.context.supertitle = u'New York'
    context.context.title = u'Standard & Poor´s'

    monkeypatch.setattr(
        zeit.content.article.interfaces, 'IArticle', lambda c, _: c)
    image = zeit.web.core.image.HeaderBlockImage(context)
    image.caption = u'Standard & Poor´s Zentrale in New York'

    assert image.alt == u'New York: Standard & Poor´s Zentrale in New York'


def test_image_should_render_caption_in_alt_tag(monkeypatch):
    context = mock.Mock()
    context.context.supertitle = None
    context.context.title = u'Standard & Poor´s'

    monkeypatch.setattr(
        zeit.content.article.interfaces, 'IArticle', lambda c, _: c)
    image = zeit.web.core.image.HeaderBlockImage(context)
    image.caption = u'Standard & Poor´s Zentrale in New York'

    assert image.alt == u'Standard & Poor´s Zentrale in New York'


def test_image_should_render_supertitle_and_title_in_alt_tag(monkeypatch):
    context = mock.Mock()
    context.context.supertitle = u'New York'
    context.context.title = u'Standard & Poor´s'

    monkeypatch.setattr(
        zeit.content.article.interfaces, 'IArticle', lambda c, _: c)
    image = zeit.web.core.image.HeaderBlockImage(context)
    image.caption = None

    assert image.alt == u'New York: Standard & Poor´s'


def test_image_should_not_break_on_missing_caption(application):
    model_block = mock.Mock()
    model_block.display_mode = 'large'
    model_block.variant_name = 'wide'
    model_block.is_empty = False
    xml = ('<image base-id="http://xml.zeit.de/foo">'
           '<copyright>© Justin Lane / dpa</copyright>'
           '</image>')
    model_block.xml = lxml.etree.fromstring(xml)
    block = zeit.web.core.block.Image(model_block)
    image = zeit.web.core.interfaces.IImage(block)
    assert image.caption is None


def test_image_should_not_break_on_empty_caption(application):
    model_block = mock.Mock()
    model_block.display_mode = 'large'
    model_block.variant_name = 'wide'
    model_block.is_empty = False
    xml = ('<image base-id="http://xml.zeit.de/foo">'
           '<bu></bu>'
           '<copyright>© Justin Lane / dpa</copyright>'
           '</image>')
    model_block.xml = lxml.etree.fromstring(xml)
    block = zeit.web.core.block.Image(model_block)
    image = zeit.web.core.interfaces.IImage(block)
    assert image.caption is None


def test_image_should_not_break_on_whitespace_caption(application):
    model_block = mock.Mock()
    model_block.display_mode = 'large'
    model_block.variant_name = 'wide'
    model_block.is_empty = False
    xml = ('<image base-id="http://xml.zeit.de/foo">'
           '<bu> </bu>'
           '<copyright>© Justin Lane / dpa</copyright>'
           '</image>')
    model_block.xml = lxml.etree.fromstring(xml)
    block = zeit.web.core.block.Image(model_block)
    image = zeit.web.core.interfaces.IImage(block)
    assert image.caption is None


def test_image_should_not_break_on_missing_image(application):
    model_block = mock.Mock()
    model_block.display_mode = 'large'
    model_block.variant_name = 'default'
    model_block.is_empty = False
    model_block.xml = lxml.etree.fromstring('<image/>')
    model_block.references.target = zeit.content.image.imagegroup.ImageGroup()
    # We use an otherwise empty folder to simulate missing master image.
    model_block.references.target.uniqueId = 'http://xml.zeit.de/news'
    block = zeit.web.core.block.Image(model_block)
    image = zeit.web.core.interfaces.IImage(block)
    assert not image


def test_image_should_use_variant_given_on_layout(application):
    image = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/image'
        '/filmstill-hobbit-schlacht-fuenf-hee/')
    model_block = mock.Mock()
    model_block.display_mode = 'column-width'
    model_block.variant_name = 'original'
    model_block.is_empty = False
    model_block.xml = lxml.etree.fromstring('<image/>')
    model_block.references.target = image
    block = zeit.web.core.block.Image(model_block)
    image = zeit.web.core.interfaces.IImage(block)
    assert image.variant_id == 'original'


def test_image_should_use_variant_original_if_infographic(application):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/infographic')
    block = zeit.web.core.article.pages_of_article(article)[0][2]
    assert block.block_type == 'infographic'
    image = zeit.web.core.interfaces.IImage(block)
    assert image.variant_id == 'original'


def test_image_should_be_none_if_expired(application):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/article/article-with-expired-image')
    image = zeit.web.core.interfaces.IImage(article)
    assert zeit.web.core.template.expired(image) is True
    image = zeit.web.core.template.get_image(article, fallback=False)
    assert image is None


def test_image_should_pass_through_ratio(application):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/article/all-blocks')
    block = zeit.web.core.article.pages_of_article(article)[0][5]
    image = zeit.web.core.interfaces.IImage(block)
    assert round(1.77 - image.ratio, 1) == 0
    assert not image.mobile_ratio


def test_image_should_set_mobile_ratio_for_variant_original(application):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/article/infographic')
    block = zeit.web.core.article.pages_of_article(article)[0][2]
    image = zeit.web.core.interfaces.IImage(block)
    assert round(0.80 - image.mobile_ratio, 1) == 0
    assert round(1.62 - image.ratio, 1) == 0


def test_module_class_should_hash_as_expected():
    context = mock.Mock()
    context.xml.attrib = {'{http://namespaces.zeit.de/CMS/cp}__name__': 42}
    mod = zeit.web.core.centerpage.Module(context)
    assert hash(mod) == 42


def test_cpextra_module_should_have_a_layout_attribute():
    context = mock.Mock()
    context.cpextra = 'lorem-ipsum'
    zope.interface.declarations.alsoProvides(
        context, zeit.content.cp.interfaces.ICPExtraBlock)
    module = zeit.web.core.centerpage.Module(context)
    assert module._layout.id == 'lorem-ipsum'


def test_vivi_module_should_have_a_layout_attribute():
    context = mock.Mock()
    context.type = 'barbapapa'
    zope.interface.declarations.alsoProvides(
        context, zeit.edit.interfaces.IBlock)
    module = zeit.web.core.centerpage.Module(context)
    assert module._layout.id == 'barbapapa'


def test_block_liveblog_instance_causing_timeouts(
        application, mockserver, monkeypatch):

    # Disable caching
    new_cache = copy.copy(pyramid_dogpile_cache2.CACHE_REGIONS)
    new_cache['long_term'] = dogpile.cache.make_region(
        'long_term',
        function_key_generator=pyramid_dogpile_cache2.cache.key_generator,
        key_mangler=pyramid_dogpile_cache2.cache.sha1_mangle_key).configure(
            'dogpile.cache.null')
    monkeypatch.setattr(pyramid_dogpile_cache2, 'CACHE_REGIONS', new_cache)

    model_block = mock.Mock()
    model_block.blog_id = '158'
    liveblog = zeit.web.core.block.Liveblog(model_block)
    assert liveblog.id == '158'
    assert liveblog.last_modified.isoformat() == (
        '2015-03-20T12:26:00+01:00')

    model_block = mock.Mock()
    model_block.blog_id = '213-259'
    liveblog = zeit.web.core.block.Liveblog(model_block)
    assert liveblog.id == '213'
    assert liveblog.is_live

    model_block = mock.Mock()
    model_block.blog_id = '166-201'
    liveblog = zeit.web.core.block.Liveblog(model_block)
    assert liveblog.id == '166'
    assert liveblog.seo_id == '201'
    assert liveblog.last_modified.isoformat() == (
        '2015-05-06T22:46:00+02:00')

    # Set unachievable timeout
    mockserver.settings['sleep'] = 1
    conf = zope.component.queryUtility(zeit.web.core.interfaces.ISettings)
    conf['liveblog_timeout'] = 0.001

    model_block = mock.Mock()
    model_block.blog_id = '166-201'
    liveblog = zeit.web.core.block.Liveblog(model_block)
    # requests failed, last_modified is not set
    assert liveblog.last_modified is None


def test_block_breaking_news_has_correct_date(application):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    view = zeit.web.site.view_article.Article(
        content, pyramid.testing.DummyRequest())

    breaking_news = zeit.web.core.block.BreakingNews()
    assert breaking_news.date_first_released == view.date_first_released


def test_block_citation_should_contain_expected_structure(tplbrowser):
    block = mock.Mock()
    block.text = u'Lorem ipsum dülör sit amet, consetetur sadipscing elitr'
    browser = tplbrowser(
        'zeit.web.core:templates/inc/blocks/citation.html',
        block=block)
    assert browser.cssselect(
        'figure.quote blockquote.quote__text')
    assert browser.cssselect('blockquote.quote__text')[0].text.strip() == (
        u'Lorem ipsum dülör sit amet, consetetur sadipscing elitr')


def test_block_contentadblock_should_contain_expected_structure(tplbrowser):
    view = mock.Mock()
    browser = tplbrowser(
        'zeit.web.core:templates/inc/blocks/contentadblock.html', view=view)
    assert browser.cssselect('div#iq-artikelanker')


def test_block_contentadblock_isnt_shown_when_content_ad_enabled_is_false(
        tplbrowser):
    view = mock.Mock()
    view.content_ad_enabled = False
    browser = tplbrowser(
        'zeit.web.core:templates/inc/blocks/contentadblock.html', view=view)
    assert not browser.cssselect('div#iq-artikelanker')


def test_block_image_should_contain_expected_structure(
        tplbrowser, dummy_request, application):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-magazin/article/inline-imagegroup')
    block = zeit.web.core.article.pages_of_article(article)[1][0]
    browser = tplbrowser(
        'zeit.web.core:templates/inc/blocks/image.html',
        block=block, request=dummy_request)
    assert browser.cssselect('img.article__media-item')


def test_block_infobox_should_contain_expected_structure(tplbrowser):
    view = mock.Mock()
    view.package = 'zeit.web.site'
    block = mock.Mock()
    block.title = 'Infobox-Titel'
    block.identifier = 'infobox-file'
    block.contents = (('Infos', 'Hier die Infos über'),)
    browser = tplbrowser(
        'zeit.web.core:templates/inc/blocks/infobox.html', block=block,
        view=view)
    assert browser.cssselect('aside.infobox.js-infobox')
    assert browser.cssselect('aside.infobox.js-infobox')[0].get('id') == (
        'infobox-file')


def test_block_inlinegallery_should_contain_expected_structure(tplbrowser):
    view = mock.Mock()
    view.package = 'zeit.web.site'
    block = {0: mock.Mock()}
    browser = tplbrowser(
        'zeit.web.core:templates/inc/blocks/gallery.html', block=block,
        view=view)
    assert browser.cssselect('div.inline-gallery')


def test_block_intertitle_should_contain_expected_structure(tplbrowser):
    browser = tplbrowser(
        'zeit.web.core:templates/inc/blocks/intertitle.html')
    assert browser.cssselect('h2.article__subheading.article__item')


def test_block_liveblog_should_contain_expected_structure(tplbrowser):
    block = mock.Mock()
    browser = tplbrowser(
        'zeit.web.core:templates/inc/blocks/liveblog.html', block=block)
    assert browser.cssselect('div.liveblog')


def test_block_orderedlist_should_contain_expected_structure(tplbrowser):
    block = mock.Mock()
    browser = tplbrowser(
        'zeit.web.core:templates/inc/blocks/orderedlist.html', block=block)
    assert browser.cssselect('ol.list.article__item')


def test_block_paragraph_should_contain_expected_structure(tplbrowser):
    browser = tplbrowser(
        'zeit.web.core:templates/inc/blocks/paragraph.html',
        block=u'Lorem ipsum dülör sit amet, consetetur sadipscing elitr')
    assert browser.cssselect('p.paragraph.article__item')
    assert browser.cssselect('p.paragraph.article__item')[0].text.strip() == (
        u'Lorem ipsum dülör sit amet, consetetur sadipscing elitr')


def test_block_place_should_contain_expected_structure(tplbrowser):
    view = mock.Mock()
    view.advertising_enabled = True
    view.package = 'zeit.web.core'
    view.banner_channel = {}
    block = mock.Mock()
    block.on_page_nr = 1
    block.tile = 7
    block.type = 'mobile'
    browser = tplbrowser(
        'zeit.web.core:templates/inc/blocks/place.html', view=view,
        block=block)
    assert browser.cssselect('script[type="text/javascript"]')


def test_block_authorbox_should_contain_expected_structure(tplbrowser):
    block = mock.Mock()
    browser = tplbrowser(
        'zeit.web.core:templates/inc/blocks/authorbox.html', block=block)
    assert browser.cssselect(
        '.authorbox.article__item.article__item--marginalia')


def test_block_portraitbox_should_contain_expected_structure(tplbrowser):
    block = mock.Mock()
    browser = tplbrowser(
        'zeit.web.core:templates/inc/blocks/portraitbox.html', block=block)
    assert browser.cssselect(
        '.portraitbox.article__item.article__item--marginalia')


def test_block_portraitbox_should_render_without_reference(testbrowser):
    browser = testbrowser('/zeit-online/article/portraitbox_inline')
    assert browser.cssselect('.portraitbox__heading')[0].text == 'Kai Biermann'
    assert (browser.cssselect('.portraitbox__body')[0].text ==
            u'Studierter Psychologe, längst aber Journalist')


def test_block_portraitbox_should_render_nothing_for_invalid_reference(
        testbrowser):
    browser = testbrowser('/zeit-online/article/portraitbox_invalid')
    assert 'Portraitbox' in browser.cssselect(
        '.article-heading__title')[0].text
    assert not browser.cssselect('.portraitbox__heading')


def test_block_quiz_should_contain_expected_structure(tplbrowser):
    block = mock.Mock()
    browser = tplbrowser(
        'zeit.web.core:templates/inc/blocks/quiz.html', block=block)
    assert browser.cssselect(
        'div.article__item.article__item--wide.article__item--rimless')


def test_block_raw_should_contain_expected_structure(tplbrowser):
    block = mock.Mock()
    browser = tplbrowser(
        'zeit.web.core:templates/inc/blocks/raw.html', block=block)
    assert browser.cssselect('div.raw')


def test_block_unorderedlist_should_contain_expected_structure(tplbrowser):
    block = mock.Mock()
    browser = tplbrowser(
        'zeit.web.core:templates/inc/blocks/unorderedlist.html', block=block)
    assert browser.cssselect('ul.list.article__item')


def test_block_video_should_contain_expected_structure(tplbrowser):
    block = mock.Mock()
    block.supertitle = 'supertitle'
    block.title = 'title'
    browser = tplbrowser(
        'zeit.web.core:templates/inc/blocks/video.html', block=block)
    assert browser.cssselect(
        'figure.article__item.article__item--wide.article__item--rimless')


def test_article_should_render_raw_code(testbrowser):
    browser = testbrowser('/zeit-online/article/raw_code')
    assert browser.cssselect('code')[0].text == 'code'


def test_find_nextread_returns_none_if_nonexistent(application):
    assert zeit.web.core.block.find_nextread_folder('Wissen', None) is None


def test_find_nextread_from_ressort_without_subressort(application):
    assert 'jobs' in zeit.web.core.block.find_nextread_folder(
        'Wirtschaft', None)


def test_find_nextread_empty_string_subressort(application):
    # DAV properties return '' instead of None when their value is unset.
    calls = []

    def find(self, *args, **kw):
        calls.append(object())
        return original_find(self, *args, **kw)
    original_find = zeit.web.core.article.RESSORTFOLDER_SOURCE.find
    zeit.web.core.article.RESSORTFOLDER_SOURCE.find = find
    assert 'jobs' in zeit.web.core.block.find_nextread_folder(
        'Wirtschaft', '')
    assert len(calls) == 1


def test_find_nextread_from_subressort(application):
    assert 'jobs' in zeit.web.core.block.find_nextread_folder(
        'Deutschland', 'Datenschutz')


def test_find_nextread_from_ressort_if_subressort_has_no_folder(application):
    assert 'jobs' in zeit.web.core.block.find_nextread_folder(
        'Deutschland', 'Integration')


def test_find_nextread_from_ressort_if_subressort_folder_is_empty(application):
    assert 'jobs' in zeit.web.core.block.find_nextread_folder(
        'Deutschland', 'Osten')


def test_find_nextread_from_correct_ressort_if_subressort_has_same_name(
        application):
    folder = zeit.web.core.block.find_nextread_folder('Deutschland', 'Meinung')
    assert 'deutsch' in list(folder.values())[0].title


def test_find_nextread_does_not_break_on_umlauts(application):
    # Assert nothing raised
    zeit.web.core.block.find_nextread_folder(u'Deutschländ', u'Datenschütz')


def test_paragraph_should_have_expected_length():
    model_block = mock.Mock()
    model_block.xml = lxml.etree.fromstring(u'<p>foo <b>baa</b></p>')
    p = zeit.web.core.block.Paragraph(model_block)
    assert len(p) == 7

    model_block = mock.Mock()
    model_block.xml = lxml.etree.fromstring(u'<p>ü</p>')
    p = zeit.web.core.block.Paragraph(model_block)
    assert len(p) == 1

    model_block = mock.Mock()
    model_block.xml = lxml.etree.fromstring(u'<p></p>')
    p = zeit.web.core.block.Paragraph(model_block)
    assert len(p) == 0

    model_block = mock.Mock()
    model_block.xml = lxml.etree.fromstring(
        u'<p><strong><em>foo</em></strong></p>')
    p = zeit.web.core.block.Paragraph(model_block)
    assert len(p) == 3


def test_volume_should_ignore_invalid_references(application):
    article = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/volumeteaser')
    article.xml.xpath('//volume')[0].set('href', 'http://xml.zeit.de/invalid')
    body = zeit.content.article.edit.interfaces.IEditableBody(article)
    module = body.values()[1]
    assert zeit.web.core.interfaces.IFrontendBlock(module, None) is None
