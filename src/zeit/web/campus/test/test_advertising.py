import pyramid.testing

import zeit.cms.interfaces
import zeit.web.core.interfaces


def test_campus_adcontroller_values_return_values_on_hp(application):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/index')
    adcv = [
        ('$handle', 'index'),
        ('level2', 'campus'),
        ('level3', ''),
        ('level4', ''),
        ('$autoSizeFrames', True),
        ('keywords', 'zeitonline'),
        ('tma', '')]
    view = view = zeit.web.campus.view_article.Article(
        content, pyramid.testing.DummyRequest(path='/campus/index'))
    assert adcv == view.adcontroller_values


def test_campus_adcontroller_values_return_values_on_cp(application):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/centerpage')
    adcv = [
        ('$handle', 'centerpage'),
        ('level2', 'campus'),
        ('level3', 'thema'),
        ('level4', 'bafoeg'),
        ('$autoSizeFrames', True),
        ('keywords', 'zeitonline'),
        ('tma', '')]
    view = view = zeit.web.campus.view_article.Article(
        content, pyramid.testing.DummyRequest())
    assert adcv == view.adcontroller_values


def test_campus_adcontroller_values_return_values_on_article(application):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/article-simple')
    adcv = [
        ('$handle', 'artikel'),
        ('level2', 'campus'),
        ('level3', 'thema'),
        ('level4', 'bafoeg'),
        ('$autoSizeFrames', True),
        ('keywords', 'zeitonline'),
        ('tma', '')]
    view = view = zeit.web.campus.view_article.Article(
        content, pyramid.testing.DummyRequest())
    assert adcv == view.adcontroller_values
