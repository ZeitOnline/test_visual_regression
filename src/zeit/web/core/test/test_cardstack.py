import urlparse

import pytest
import zope.component

import zeit.web.core.interfaces


@pytest.mark.parametrize('path_fragment', ['zeit-online', 'campus'])
def test_cardstack_should_be_included_on_articles(
        app_settings, testbrowser, path_fragment):
    browser = testbrowser('/{}/article/cardstack'.format(path_fragment))
    espi = app_settings['cardstack_backend']

    assert browser.document.xpath('head/include/@src')[0] == (
        '{}/stacks/esi/head'.format(espi))

    assert browser.document.xpath('head/meta[@name="twitter:site"]')

    src = browser.document.xpath('body//article//include/@src')[0]
    parts = urlparse.urlparse(src)
    query = urlparse.parse_qs(parts.query)
    assert 'http://' + parts.netloc + parts.path == (
        '{}/stacks/kekse/esi/body'.format(espi))
    assert query == {
        'shareUrlQuerySuffix': ['stackId=kekse'],
        'shareUrl': ['http://localhost/{}/article/cardstack'.format(
            path_fragment)]
    }

    assert browser.document.xpath('body/include/@src')[0] == (
        '{}/stacks/esi/scripts'.format(espi))


def test_cardstack_should_honor_article_stack_id(app_settings, testbrowser):
    browser = testbrowser('/zeit-online/article/cardstack?stackId=kekse')
    espi = app_settings['cardstack_backend']

    assert browser.document.xpath('head/include/@src')[0] == (
        '{}/stacks/kekse/esi/head'.format(espi))

    assert not browser.document.xpath('head/meta[@name="twitter:site"]')

    src = browser.document.xpath('body//article//include/@src')[0]
    parts = urlparse.urlparse(src)
    query = urlparse.parse_qs(parts.query)
    assert 'http://' + parts.netloc + parts.path == (
        '{}/stacks/kekse/esi/body'.format(espi))
    assert query == {
        'shareUrlQuerySuffix': ['stackId=kekse'],
        'shareUrl': ['http://localhost/zeit-online/article/cardstack'],
    }

    assert browser.document.xpath('body/include/@src')[0] == (
        '{}/stacks/esi/scripts'.format(espi))


def test_missing_cardstacks_should_not_be_included(testbrowser):
    article = testbrowser('/zeit-online/article/01').document

    settings = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    assert not article.xpath('head/include/@src')
    assert not article.xpath('body//article//include/@src')
    assert not article.xpath(
        'body/include[contains(@src, "%s")]' % settings['cardstack_backend'])

    cp = testbrowser('/zeit-online/slenderized-centerpage').document

    assert not cp.xpath('head/include/@src')
    assert not cp.xpath('body//main//include/@src')
    assert not cp.xpath(
        'body/include[contains(@src, "%s")]' % settings['cardstack_backend'])


def test_cardstack_should_be_included_on_cps(app_settings, testbrowser):
    browser = testbrowser('/index')
    espi = app_settings['cardstack_backend']

    assert browser.document.xpath('head/include/@src')[0] == (
        '{}/stacks/esi/head?static=true'.format(espi))

    assert browser.document.xpath('body//main//include/@src')[0] == (
        '{}/stacks/kekse/esi/body?shareUrlQuerySuffix=stackId%3Dkekse'
        '&static=true'.format(espi))

    assert browser.document.xpath('body/include/@src')[0] == (
        '{}/stacks/esi/scripts'.format(espi))

    browser = testbrowser('/campus/centerpage/cardstack')

    assert browser.document.xpath('head/include/@src')[0] == (
        '{}/stacks/esi/head?static=true'.format(espi))

    assert browser.document.xpath('body//main//include/@src')[0] == (
        '{}/stacks/erkaeltung-hausmittel-wirkung/esi/body?'
        'shareUrlQuerySuffix=stackId%3Derkaeltung-hausmittel-wirkung'
        '&static=true'.format(espi))

    assert browser.document.xpath('body/include/@src')[0] == (
        '{}/stacks/esi/scripts'.format(espi))


def test_cardstack_should_honor_cp_stack_id(app_settings, testbrowser):
    browser = testbrowser('/index?stackId=kekse')
    espi = app_settings['cardstack_backend']

    assert browser.document.xpath('head/include/@src')[0] == (
        '{}/stacks/kekse/esi/head?static=true'.format(espi))

    assert not browser.document.xpath('head/meta[@name="twitter:site"]')

    assert browser.document.xpath('body//main//include/@src')[0] == (
        '{}/stacks/kekse/esi/body?shareUrlQuerySuffix='
        'stackId%3Dkekse&static=true'.format(espi))

    assert browser.document.xpath('body/include/@src')[0] == (
        '{}/stacks/esi/scripts'.format(espi))


def test_cardstack_article_should_still_have_site_name_and_admin_meta_tag(
        testbrowser):
    doc = testbrowser('/zeit-online/article/cardstack?stackId=kekse').document
    assert doc.xpath('head/meta[@property="og:site_name"]/@content')[0] == (
        'ZEIT ONLINE')
    assert doc.xpath('head/meta[@property="fb:admins"]/@content')[0] == (
        '595098294')
