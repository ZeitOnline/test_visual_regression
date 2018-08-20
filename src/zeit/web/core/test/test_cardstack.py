import urlparse

import pytest
import zope.component

import zeit.web.core.interfaces


@pytest.mark.parametrize('path_fragment', ['zeit-online', 'campus'])
def test_cardstack_should_be_included_on_articles(
        app_settings, testbrowser, path_fragment):
    browser = testbrowser('/{}/article/cardstack'.format(path_fragment))

    assert browser.document.xpath('head/include/@src')[0] == (
        '/cardstack-backend/stacks/esi/head')

    assert browser.document.xpath('head/meta[@name="twitter:site"]')

    src = browser.document.xpath('body//article//include/@src')[0]
    assert src.startswith(
        '/cardstack-backend/stacks/erkaeltung-hausmittel-wirkung/esi/body')
    query = urlparse.parse_qs(urlparse.urlparse(src).query)
    assert query == {
        'shareUrlQuerySuffix': ['stackId=erkaeltung-hausmittel-wirkung'],
        'shareUrl': ['http://localhost/{}/article/cardstack'.format(
            path_fragment)]
    }

    assert browser.document.xpath(
        'body/include[@src="/cardstack-backend/stacks/esi/scripts"]')


# We test nothing with using the same stackId as query parameter
# like stated in the page XML, do we?
# @pytest.mark.xfail(reason='Maybe this never worked')
def test_cardstack_should_honor_article_stack_id(app_settings, testbrowser):
    browser = testbrowser(
        '/zeit-online/article/cardstack?stackId=erkaeltung-hausmittel-wirkung')

    assert browser.document.xpath('head/include/@src')[0] == (
        '/cardstack-backend/stacks/erkaeltung-hausmittel-wirkung/esi/head')

    assert not browser.document.xpath('head/meta[@name="twitter:site"]')

    src = browser.document.xpath('body//article//include/@src')[0]
    assert src.startswith(
        '/cardstack-backend/stacks/erkaeltung-hausmittel-wirkung/esi/body')
    query = urlparse.parse_qs(urlparse.urlparse(src).query)
    assert query == {
        'shareUrlQuerySuffix': ['stackId=erkaeltung-hausmittel-wirkung'],
        'shareUrl': ['http://localhost/zeit-online/article/cardstack'],
    }

    assert browser.document.xpath(
        'body/include[@src="/cardstack-backend/stacks/esi/scripts"]')


def test_missing_cardstacks_should_not_be_included(testbrowser):
    article = testbrowser('/zeit-online/article/01').document

    assert not article.xpath('head/include/@src')
    assert not article.xpath('body//article//include/@src')
    assert not article.xpath(
        'body/include[contains(@src, "/cardstack-backend")]')

    cp = testbrowser('/zeit-online/slenderized-centerpage').document

    assert not cp.xpath('head/include/@src')
    assert not cp.xpath('body//main//include/@src')
    assert not cp.xpath(
        'body/include[contains(@src, "/cardstack-backend")]')


def test_cardstack_should_be_included_on_cps(app_settings, testbrowser):
    browser = testbrowser('/index')

    assert browser.document.xpath('head/include/@src')[0] == (
        '/cardstack-backend/stacks/esi/head?static=true')

    assert browser.document.xpath('body//main//include/@src')[0] == (
        '/cardstack-backend/stacks/kekse/esi/body'
        '?shareUrlQuerySuffix=stackId%3Dkekse&static=true')

    assert browser.document.xpath(
        'body/include[@src="/cardstack-backend/stacks/esi/scripts"]')

    browser = testbrowser('/campus/centerpage/cardstack')

    assert browser.document.xpath('head/include/@src')[0] == (
        '/cardstack-backend/stacks/esi/head?static=true')

    assert browser.document.xpath('body//main//include/@src')[0] == (
        '/cardstack-backend/stacks/erkaeltung-hausmittel-wirkung/esi/body?'
        'shareUrlQuerySuffix=stackId%3Derkaeltung-hausmittel-wirkung'
        '&static=true')

    assert browser.document.xpath(
        'body/include[@src="/cardstack-backend/stacks/esi/scripts"]')


def test_cardstack_should_honor_cp_stack_id(app_settings, testbrowser):
    browser = testbrowser('/index?stackId=kekse')

    assert browser.document.xpath('head/include/@src')[0] == (
        '/cardstack-backend/stacks/kekse/esi/head?static=true')

    assert not browser.document.xpath('head/meta[@name="twitter:site"]')

    assert browser.document.xpath('body//main//include/@src')[0] == (
        '/cardstack-backend/stacks/kekse/esi/body?shareUrlQuerySuffix='
        'stackId%3Dkekse&static=true')

    assert browser.document.xpath(
        'body/include[@src="/cardstack-backend/stacks/esi/scripts"]')


def test_cardstack_article_should_still_have_site_name_and_admin_meta_tag(
        testbrowser):
    doc = testbrowser('/zeit-online/article/cardstack?stackId=kekse').document
    assert doc.xpath('head/meta[@property="og:site_name"]/@content')[0] == (
        'ZEIT ONLINE')
    assert doc.xpath('head/meta[@property="fb:app_id"]/@content')[0] == (
        '638028906281625')
