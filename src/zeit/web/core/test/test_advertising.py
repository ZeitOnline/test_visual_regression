# -*- coding: utf-8 -*-
import mock
import pytest

import pyramid.request

import zope.component

import zeit.web.core.application


@pytest.fixture
def mock_ad_view(application):
    class MockAdView(zeit.web.core.view.Base):

        def __init__(
                self, type, ressort,
                sub_ressort, is_hp=False, banner_id=None, serienname='',
                product_id=None,
                path_info=None, adv_title=''):
            self.type = type
            self.ressort = ressort
            self.sub_ressort = sub_ressort
            self.is_hp = is_hp
            self.product_id = product_id
            self.serie = serienname
            context = mock.Mock()
            context.banner_id = banner_id
            context.advertisement_title = adv_title
            product_source = zeit.cms.content.interfaces.ICommonMetadata[
                'product'].source(None)
            context.product = product_source.find(product_id)
            context.keywords = []
            request = pyramid.testing.DummyRequest()
            request.path_info = path_info
            self.request = request
            self.context = context

            # fake zeit.web.magazin.view.Base property
            # this starts to get kind of overmocked ... [ms]
            if self.ressort == 'zeit-magazin':
                self.adwords = ['zeitonline', 'zeitmz']

    return MockAdView


def test_iqd_ads_should_utilize_feature_toggles(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set('iqd', 'third_party_modules')
    browser = testbrowser('/zeit-online/article/zeit')
    assert 'AdController.initialize();' in (
        browser.cssselect('head')[0].text_content())

    zeit.web.core.application.FEATURE_TOGGLES.unset(
        'iqd', 'third_party_modules')
    browser = testbrowser('/zeit-online/article/zeit')
    assert 'AdController.initialize();' not in (
        browser.cssselect('head')[0].text_content())

    zeit.web.core.application.FEATURE_TOGGLES.set('iqd')
    zeit.web.core.application.FEATURE_TOGGLES.unset('third_party_modules')
    browser = testbrowser('/zeit-online/article/zeit')
    assert 'AdController.initialize();' not in (
        browser.cssselect('head')[0].text_content())


def test_ads_should_utilize_settings(testbrowser):
    selector = '#iq-artikelanker'
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    conf['ctm_teaser_ressorts'] = ''
    browser = testbrowser('/zeit-online/article/zeit')
    assert len(browser.cssselect(selector)) == 0

    conf['ctm_teaser_ressorts'] = 'Gesellschaft'
    browser = testbrowser('/zeit-online/article/zeit')
    assert len(browser.cssselect(selector)) == 1


def test_adcontroller_handles_for_entdecken_und_reisen(mock_ad_view):
    assert mock_ad_view(
        'centerpage', 'entdecken', ''
    ).adcontroller_handle.startswith('index')
    assert mock_ad_view(
        'centerpage', 'entdecken', 'reisen'
    ).adcontroller_handle.startswith('centerpage')
    assert mock_ad_view(
        'article', 'entdecken', ''
    ).adcontroller_handle.startswith('artikel')
    assert mock_ad_view(
        'article', 'entdecken', 'reisen'
    ).adcontroller_handle.startswith('artikel')


def test_adcontroller_banner_channel_for_entdecken_und_reisen(mock_ad_view):
    assert mock_ad_view(
        'centerpage', 'entdecken', ''
    ).banner_channel == 'reisen/centerpage'
    assert mock_ad_view(
        'centerpage', 'entdecken', 'reisen'
    ).banner_channel == 'reisen/centerpage'


def test_adcontroller_handle_return_value(mock_ad_view):
    assert mock_ad_view(
        'centerpage', 'politik', ''
    ).adcontroller_handle.startswith('index')
    assert mock_ad_view(
        'centerpage', 'zeit-magazin', ''
    ).adcontroller_handle.startswith('index')
    assert mock_ad_view(
        'centerpage', 'homepage', '', is_hp=True
    ).adcontroller_handle.startswith('homepage')
    assert mock_ad_view(
        'centerpage', 'politik', 'deutschland'
    ).adcontroller_handle.startswith('centerpage')
    assert mock_ad_view(
        'article', 'politik', 'deutschland'
    ).adcontroller_handle.startswith('artikel')
    assert mock_ad_view(
        'video', 'politik', 'deutschland'
    ).adcontroller_handle.startswith('video_artikel')
    assert mock_ad_view(
        'quiz', 'politik', 'deutschland'
    ).adcontroller_handle.startswith('quiz')


def test_banner_channel_mapping_should_apply_first_rule(mock_ad_view):
    assert mock_ad_view(
        'centerpage', 'angebote', '',
        banner_id='mein/ad/code').banner_channel == 'mein/ad/code/centerpage'


def test_banner_channel_mapping_should_apply_second_rule(mock_ad_view):
    assert mock_ad_view(
        'centerpage', 'angebote', '', serienname='meh').banner_channel == (
            'adv/angebote/centerpage')
    assert mock_ad_view(
        'centerpage', 'angebote', '', adv_title='Foo Bar').banner_channel == (
            'adv/foobar/centerpage')
    assert mock_ad_view(
        'centerpage', 'angebote', '',
        banner_id='mcs/xx/yy').banner_channel == ('mcs/xx/yy/centerpage')


def test_banner_channel_mapping_by_path_info(mock_ad_view):
    assert mock_ad_view(
        'centerpage', '', '',
        path_info='/serie/krimizeit-bestenliste').banner_channel == (
            'literatur/krimi-bestenliste/centerpage')


def test_banner_channel_mapping_should_apply_third_rule(mock_ad_view):
    assert mock_ad_view(
        'centerpage', 'zeit-magazin', 'irgendwas'
    ).banner_channel == 'zeitmz/irgendwas/centerpage'
    assert mock_ad_view(
        'centerpage', 'lebensart', ''
    ).banner_channel == 'zeitmz/centerpage'
    assert mock_ad_view(
        'centerpage', 'mobilitaet', ''
    ).banner_channel == 'auto/centerpage'
    assert mock_ad_view(
        'centerpage', 'ranking', ''
    ).banner_channel == 'studium/centerpage'
    assert mock_ad_view(
        'centerpage', 'sport', '', product_id='news'
    ).banner_channel == 'news/centerpage'
    assert mock_ad_view(
        'centerpage', 'politk', '', product_id='sid'
    ).banner_channel == 'sid/centerpage'
    assert mock_ad_view(
        'article', 'foto', ''
    ).banner_channel == 'kultur/article'
    assert mock_ad_view(
        'article', 'wirtschaft', 'geld', serienname='geldspezial'
    ).banner_channel == 'geldspezial/article'
    assert mock_ad_view(
        'centerpage', 'sport', 'zeit wissen'
    ).banner_channel == 'wissen/zeit_wissen/centerpage'
    assert mock_ad_view(
        'centerpage', 'sport', 'zeit campus'
    ).banner_channel == 'wissen/zeit_campus/centerpage'
    assert mock_ad_view(
        'centerpage', 'sport', 'zeit geschichte'
    ).banner_channel == 'wissen/zeit_geschichte/centerpage'
    assert mock_ad_view(
        'centerpage', 'sport', 'das wissen dieser welt'
    ).banner_channel == 'wissen/bildungskanon/centerpage'
    assert mock_ad_view(
        'centerpage', 'wissen', '', serienname="spiele"
    ).banner_channel == 'spiele/centerpage'
    assert mock_ad_view(
        'centerpage', 'campus', 'irgendwas'
    ).banner_channel == 'studium/irgendwas/centerpage'
    assert mock_ad_view(
        'centerpage', 'wissen', '', serienname="reise"
    ).banner_channel == 'reisen/centerpage'
    assert mock_ad_view(
        'centerpage', 'kultur', 'computer'
    ).banner_channel == 'digital/centerpage'
    assert mock_ad_view(
        'centerpage', 'technik', ''
    ).banner_channel == 'digital/centerpage'


def test_banner_channel_mapping_should_apply_fourthandfitfth(mock_ad_view):
    assert mock_ad_view(
        'centerpage', 'politik', '').banner_channel == 'politik/centerpage'
    assert mock_ad_view(
        'centerpage', 'pol', 'deu').banner_channel == 'pol/deu/centerpage'


def test_banner_channel_mapping_should_apply_last_rule(mock_ad_view):
    assert mock_ad_view(
        'centerpage', '', '').banner_channel == 'vermischtes/centerpage'


def test_adcontroller_values_are_correctly_returned(mock_ad_view):
    zw_code = [('$handle', 'centerpage_trsf'), ('level2', 'wissen'),
               ('level3', 'zeit_wissen'), ('level4', ''),
               ('$autoSizeFrames', True), ('keywords', 'zeitonline'),
               ('tma', '')]
    zw_test = mock_ad_view(
        'centerpage', 'sport', 'zeit wissen').adcontroller_values
    assert zw_code == zw_test
    zmz_code = [('$handle', 'index_trsf'), ('level2', 'zeitmz'),
                ('level3', 'irgendwas'), ('level4', ''),
                ('$autoSizeFrames', True), ('keywords', 'zeitonline,zeitmz'),
                ('tma', '')]
    zmz_test = mock_ad_view(
        'centerpage', 'zeit-magazin', 'irgendwas').adcontroller_values
    assert zmz_code == zmz_test
    zw_code = [('$handle', 'centerpage_trsf'), ('level2', 'studium'),
               ('level3', 'unileben'), ('level4', ''),
               ('$autoSizeFrames', True), ('keywords', 'zeitonline'),
               ('tma', '')]
    zw_test = mock_ad_view(
        'centerpage', 'studium', 'uni-leben').adcontroller_values
    assert zw_code == zw_test


def test_adcontroller_values_for_stimmts_series(mock_ad_view):
    adv_test = mock_ad_view(
        'article', 'wissen', '', serienname='Stimmt\'s').adcontroller_values
    adv_code = [('$handle', 'artikel_trsf'), ('level2', u'wissen'),
                ('level3', u'serie'), ('level4', 'stimmts'),
                ('$autoSizeFrames', True), ('keywords', 'zeitonline'),
                ('tma', '')]
    assert adv_test == adv_code


def test_banner_advertorial_extrarulez(mock_ad_view):
    adv_test = mock_ad_view(
        'centerpage', 'angebote',
        '', banner_id='angebote/ingdiba',
        adv_title='ingdiba', product_id='ADV').adcontroller_values
    adv_code = [('$handle', 'adv_index_trsf'), ('level2', u'angebote'),
                ('level3', u'ingdiba'), ('level4', ''),
                ('$autoSizeFrames', True), ('keywords', 'angebote,ingdiba'),
                ('tma', '')]
    assert adv_test == adv_code
