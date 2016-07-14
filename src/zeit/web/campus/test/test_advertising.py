import pyramid.testing

import zeit.cms.interfaces
import zeit.web.core.interfaces


def test_campus_adcontroller_values_return_values_on_hp(application):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/index')
    adcv = [
        ('$handle', 'homepage'),
        ('level2', 'campus'),
        ('level3', ''),
        ('level4', ''),
        ('$autoSizeFrames', True),
        ('keywords', 'zeitonline,zeitcampus'),
        ('tma', '')]
    view = zeit.web.campus.view_centerpage.Centerpage(
        content, pyramid.testing.DummyRequest(path='/campus/index'))
    assert adcv == view.adcontroller_values


def test_campus_hp_banner_channel_is_correct(application, dummy_request):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/index')
    view = zeit.web.campus.view_centerpage.Centerpage(content, dummy_request)
    assert 'centerpage' in view.banner_channel


def test_campus_adcontroller_values_return_values_on_cp(
        application, dummy_request):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/centerpage/index')
    adcv = [
        ('$handle', 'index'),
        ('level2', 'campus'),
        ('level3', ''),
        ('level4', ''),
        ('$autoSizeFrames', True),
        ('keywords', 'zeitonline,zeitcampus'),
        ('tma', '')]
    view = zeit.web.campus.view_centerpage.Centerpage(
        content, pyramid.testing.DummyRequest())
    assert adcv == view.adcontroller_values


def test_campus_adcontroller_values_return_values_on_article(application):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/article/adcontroller')
    adcv = [
        ('$handle', 'artikel'),
        ('level2', 'campus'),
        ('level3', 'thema'),
        ('level4', 'bafoeg_antraege_fuer_ue_50'),
        ('$autoSizeFrames', True),
        ('keywords', 'zeitonline,zeitcampus'),
        ('tma', '')]
    view = zeit.web.campus.view_article.Article(
        content, pyramid.testing.DummyRequest())
    assert adcv == view.adcontroller_values


def test_campus_adcontroller_values_return_values_on_advertorial_article(
        application, dummy_request):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/article/advertorial')
    adcv = [
        ('$handle', 'adv_artikel'),
        ('level2', u'adv'),
        ('level3', u'iwcschaffhausen'),
        ('level4', ''),
        ('$autoSizeFrames', True),
        ('keywords', 'zeitonline,zeitcampus'),
        ('tma', '')]
    view = zeit.web.campus.view_article.Article(content, dummy_request)
    assert adcv == view.adcontroller_values


def test_campus_adcontroller_values_return_values_on_advertorial_cp(
        application, dummy_request):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/centerpage/advertorial')
    adcv = [
        ('$handle', 'adv_index'),
        ('level2', u'adv'),
        ('level3', u'buchtipp'),
        ('level4', ''),
        ('$autoSizeFrames', True),
        ('keywords', 'zeitonline,zeitcampus'),
        ('tma', '')]
    view = zeit.web.campus.view_article.Article(content, dummy_request)
    assert adcv == view.adcontroller_values


def test_campus_adplace7_should_be_placeable_via_cpextra(testbrowser):
    browser = testbrowser('/campus/centerpage/adplace7')
    assert len(browser.cssselect('script[id="ad-desktop-7"]')) == 1


def test_campus_adcontroller_values_return_values_on_topic_cp(application):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/centerpage/thema')
    adcv = [
        ('$handle', 'index'),
        ('level2', 'campus'),
        ('level3', 'thema'),
        ('level4', 'jurastudium'),
        ('$autoSizeFrames', True),
        ('keywords', 'zeitonline,zeitcampus'),
        ('tma', '')]
    view = zeit.web.campus.view_centerpage.Centerpage(
        content, pyramid.testing.DummyRequest())
    assert adcv == view.adcontroller_values
