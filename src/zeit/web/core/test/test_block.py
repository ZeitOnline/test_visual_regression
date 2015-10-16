# -*- coding: utf-8 -*-
import beaker
import lxml.etree
import mock
import copy

import pyramid.testing
import zope.interface.declarations

import zeit.cms.interfaces
import zeit.edit.interfaces
import zeit.web.site.module
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
    model_block.video = None
    video = zeit.web.core.block.Video(model_block)
    assert not hasattr(video, 'video_still')

    model_block = mock.Mock()
    model_block.video = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/video/2015-01/3537342483001')
    video = zeit.web.core.block.Video(model_block)
    assert hasattr(video, 'video_still')


def test_header_video_should_be_created_if_layout_is_zmo_header(application):
    model_block = mock.Mock()
    model_block.layout = 'zmo-xl-header'
    model_block.video = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/video/2015-01/3537342483001')
    h_video = zeit.web.core.block.HeaderVideo(model_block)
    assert type(h_video) == zeit.web.core.block.HeaderVideo
    assert h_video.format == 'zmo-xl-header'


def test_header_video_should_not_be_created_if_layout_does_not_fit(
        application):
    model_block = mock.Mock()
    model_block.layout = 'zmo-xl-noheader'
    model_block.video = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/video/2015-01/3537342483001')

    h_video = zeit.web.core.block.HeaderVideo(model_block)
    assert h_video is None


def test_header_image_should_be_created_if_layout_is_zmo_header():
    model_block = mock.Mock()
    model_block.layout.id = 'zmo-xl-header'
    model_block.is_empty = False
    h_image = zeit.web.core.block.HeaderImage(model_block)
    assert type(h_image) == zeit.web.core.block.HeaderImage


def test_header_image_should_not_be_created_if_layout_does_not_fit():
    model_block = mock.Mock()
    model_block.layout.id = 'zmo-xl-noheader'
    model_block.is_empty = False

    h_image = zeit.web.core.block.HeaderImage(model_block)
    assert h_image is None


def test_image_should_be_none_if_is_empty_is_true():
    model_block = mock.Mock()
    model_block.layout.id = 'zmo-xl-noheader'
    model_block.is_empty = True
    image = zeit.web.core.block.Image(model_block)
    assert image is None


def test_image_should_be_fail_if_is_empty_doesnot_exist():
    model_block = mock.Mock(spec=('layout',))
    model_block.layout = mock.Mock()
    model_block.layout.id = 'zmo-xl-header'
    image = zeit.web.core.block.Image(model_block)
    assert image is None


def test_image_should_decode_html_entities_in_caption():
    model_block = mock.Mock()
    model_block.layout.id = 'large'
    model_block.is_empty = False
    xml = ('<image base-id="http://xml.zeit.de/foo">'
           '<bu>Standard &amp; Poor´s Zentrale in New York</bu>'
           '<copyright>© Justin Lane / dpa</copyright>'
           '</image>')
    model_block.xml = lxml.etree.fromstring(xml)
    image = zeit.web.core.block.Image(model_block)
    assert image.caption == u'Standard & Poor´s Zentrale in New York'


def test_image_should_not_break_on_missing_caption():
    model_block = mock.Mock()
    model_block.layout.id = 'large'
    model_block.is_empty = False
    xml = ('<image base-id="http://xml.zeit.de/foo">'
           '<copyright>© Justin Lane / dpa</copyright>'
           '</image>')
    model_block.xml = lxml.etree.fromstring(xml)
    image = zeit.web.core.block.Image(model_block)
    assert image.caption == ''


def test_image_should_not_break_on_empty_caption():
    model_block = mock.Mock()
    model_block.layout.id = 'large'
    model_block.is_empty = False
    xml = ('<image base-id="http://xml.zeit.de/foo">'
           '<bu></bu>'
           '<copyright>© Justin Lane / dpa</copyright>'
           '</image>')
    model_block.xml = lxml.etree.fromstring(xml)
    image = zeit.web.core.block.Image(model_block)
    assert image.caption == ''


def test_image_should_not_break_on_whitespace_caption():
    model_block = mock.Mock()
    model_block.layout.id = 'large'
    model_block.is_empty = False
    xml = ('<image base-id="http://xml.zeit.de/foo">'
           '<bu> </bu>'
           '<copyright>© Justin Lane / dpa</copyright>'
           '</image>')
    model_block.xml = lxml.etree.fromstring(xml)
    image = zeit.web.core.block.Image(model_block)
    assert image.caption == ''


def test_image_should_not_break_on_missing_image(application):
    model_block = mock.Mock()
    model_block.layout.id = 'large'
    model_block.layout.variant = 'large'
    model_block.is_empty = False
    model_block.xml = None
    model_block.references.target = zeit.content.image.imagegroup.ImageGroup()
    # We use an otherwise empty folder to simulate missing master image.
    model_block.references.target.uniqueId = 'http://xml.zeit.de/news'
    image = zeit.web.core.block.Image(model_block)
    assert image.image is None


def test_image_should_use_variant_given_on_layout(application):
    from zeit.content.article.edit.interfaces import imageLayoutSource
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/article/01')
    image = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/zeit-online/image'
        '/filmstill-hobbit-schlacht-fuenf-hee/')
    model_block = mock.Mock()
    model_block.layout = imageLayoutSource(content).find('large-original')
    model_block.is_empty = False
    model_block.xml = None
    model_block.references.target = image
    image = zeit.web.core.block.Image(model_block)
    assert 'original' == image.image.__name__


def test_image_should_be_none_if_expired():
    model_block = mock.Mock()
    model_block.is_empty = False
    with mock.patch('zeit.web.core.image.is_image_expired') as expired:
        expired.return_value = True
        image = zeit.web.core.block.Image(model_block)
        assert image.image is None


def test_module_class_should_hash_as_expected():
    context = mock.Mock()
    context.xml.attrib = {'{http://namespaces.zeit.de/CMS/cp}__name__': 42}
    mod = zeit.web.site.module.Module(context)
    assert hash(mod) == 42


def test_cpextra_module_should_have_a_layout_attribute():
    context = mock.Mock()
    context.cpextra = 'lorem-ipsum'
    zope.interface.declarations.alsoProvides(
        context, zeit.content.cp.interfaces.ICPExtraBlock)
    module = zeit.web.site.module.Module(context)
    assert module._layout.id == 'lorem-ipsum'


def test_vivi_module_should_have_a_layout_attribute():
    context = mock.Mock()
    context.type = 'barbapapa'
    zope.interface.declarations.alsoProvides(
        context, zeit.edit.interfaces.IBlock)
    module = zeit.web.site.module.Module(context)
    assert module._layout.id == 'barbapapa'


def test_block_liveblog_instance_causing_timeouts(application, mockserver,
                                                  monkeypatch):

    # Disable caching
    new_beaker = copy.deepcopy(beaker.cache.cache_regions)
    new_beaker.update({'long_term': {'enabled': False}})
    with mock.patch.dict(beaker.cache.cache_regions, new_beaker):
        model_block = mock.Mock()
        model_block.blog_id = '158'
        liveblog = zeit.web.core.block.Liveblog(model_block)
        assert liveblog.id == '158'
        assert liveblog.last_modified.isoformat() == (
            '2015-03-20T12:26:00+01:00')

        model_block = mock.Mock()
        model_block.blog_id = '166-201'
        liveblog = zeit.web.core.block.Liveblog(model_block)
        assert liveblog.id == '166'
        assert liveblog.seo_id == '201'
        assert liveblog.last_modified.isoformat() == (
            '2015-05-06T22:46:00+02:00')

        # Set unachievable timeout
        mockserver.settings['sleep'] = 1
        monkeypatch.setattr(zeit.web.core.block.Liveblog, 'timeout', 0.001)

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


def test_find_nextread_returns_none_if_nonexistent(application):
    adv = zeit.web.core.block.AdvertisementNextread(None)
    assert adv.find_nextread_folder('Wissen', None) is None


def test_find_nextread_from_ressort_without_subressort(application):
    adv = zeit.web.core.block.AdvertisementNextread(None)
    assert adv.find_nextread_folder('Wirtschaft', None) is not None


def test_find_nextread_from_subressort(application):
    adv = zeit.web.core.block.AdvertisementNextread(None)
    assert adv.find_nextread_folder('Deutschland', 'Datenschutz') is not None


def test_find_nextread_from_ressort_if_subressort_has_none(application):
    adv = zeit.web.core.block.AdvertisementNextread(None)
    assert adv.find_nextread_folder('Deutschland', 'Integration') is not None


def test_find_nextread_from_correct_ressort_if_subressort_has_same_name(
        application):
    adv = zeit.web.core.block.AdvertisementNextread(None)
    folder = adv.find_nextread_folder('Deutschland', 'Meinung')
    assert 'deutsch' in list(folder.values())[0].title
