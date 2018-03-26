import zeit.cms.interfaces
import zeit.web.core.interfaces


def test_campus_adcontroller_values_return_values_on_hp(
        application, dummy_request):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/index')
    adcv = [
        ('$handle', 'campus_homepage_trsf'),
        ('level2', 'campus'),
        ('level3', ''),
        ('level4', ''),
        ('$autoSizeFrames', True),
        ('keywords', 'zeitonline,zeitcampus'),
        ('tma', '')]
    view = zeit.web.campus.view_centerpage.Centerpage(content, dummy_request)
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
        ('$handle', 'index_trsf'),
        ('level2', 'campus'),
        ('level3', ''),
        ('level4', ''),
        ('$autoSizeFrames', True),
        ('keywords', 'zeitonline,zeitcampus'),
        ('tma', '')]
    view = zeit.web.campus.view_centerpage.Centerpage(content, dummy_request)
    assert adcv == view.adcontroller_values


def test_campus_adcontroller_values_return_values_on_article(
        application, dummy_request):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/article/adcontroller')
    adcv = [
        ('$handle', 'artikel_trsf'),
        ('level2', 'campus'),
        ('level3', 'thema'),
        ('level4', 'bafoeg_antraege_fuer_ue_50'),
        ('$autoSizeFrames', True),
        ('keywords', 'zeitonline,zeitcampus'),
        ('tma', '')]
    view = zeit.web.campus.view_article.Article(content, dummy_request)
    assert adcv == view.adcontroller_values


def test_campus_adcontroller_values_return_values_on_advertorial_article(
        application, dummy_request):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/article/advertorial')
    adcv = [
        ('$handle', 'adv_artikel_trsf'),
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
        ('$handle', 'adv_index_trsf'),
        ('level2', u'adv'),
        ('level3', u'buchtipp'),
        ('level4', ''),
        ('$autoSizeFrames', True),
        ('keywords', 'zeitonline,zeitcampus'),
        ('tma', '')]
    view = zeit.web.campus.view_article.Article(content, dummy_request)
    assert adcv == view.adcontroller_values


def test_campus_adplace8_should_be_placeable_via_cpextra(testbrowser):
    browser = testbrowser('/campus/centerpage/adplace8')
    assert len(browser.cssselect('script[id="ad-desktop-8"]')) == 1


def test_campus_adcontroller_values_return_values_on_topic_cp(
        application, dummy_request):
    content = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/centerpage/thema')
    adcv = [
        ('$handle', 'index_trsf'),
        ('level2', 'campus'),
        ('level3', 'thema'),
        ('level4', 'jurastudium'),
        ('$autoSizeFrames', True),
        ('keywords', 'zeitonline,zeitcampus'),
        ('tma', '')]
    view = zeit.web.campus.view_centerpage.Centerpage(content, dummy_request)
    assert adcv == view.adcontroller_values


def test_overridden_adcontroller_values(
        application, dummy_request):
    cp = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/centerpage/advertorial-with-banner-id')
    adcv = [
        ('$handle', 'adv_index_trsf'),
        ('level2', 'campus'),
        ('level3', 'angebote'),
        ('level4', '100tage'),
        ('$autoSizeFrames', True),
        ('keywords', 'zeitonline,zeitcampus'),
        ('tma', '')]
    view = zeit.web.campus.view_centerpage.Centerpage(cp, dummy_request)
    assert adcv == view.adcontroller_values


def test_adplace8_on_articles(testbrowser):
    browser = testbrowser('/campus/article/01-countdown-studium')
    assert len(browser.cssselect('#ad-desktop-8')) == 1


def test_adplace4_on_articles(testbrowser):
    browser = testbrowser('/campus/article/01-countdown-studium')
    assert len(browser.cssselect('#ad-desktop-4')) == 1


def test_adplace16_on_articles(testbrowser):
    browser = testbrowser('/campus/article/01-countdown-studium')
    assert len(browser.cssselect('#ad-desktop-16')) == 1


def test_zco_adplace5_depends_on_ligatus_toggle_on(testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'third_party_modules': True,
        'iqd': True,
        'ligatus': True
    }.get)

    browser = testbrowser('/campus/article/01-countdown-studium')
    assert not browser.cssselect('#ad-desktop-5')


def test_zco_adplace5_depends_on_ligatus_toggle_off(testbrowser, monkeypatch):
    monkeypatch.setattr(zeit.web.core.application.FEATURE_TOGGLES, 'find', {
        'third_party_modules': True,
        'iqd': True,
        'ligatus': False
    }.get)

    browser = testbrowser('/campus/article/01-countdown-studium')
    assert browser.cssselect('#ad-desktop-5')
