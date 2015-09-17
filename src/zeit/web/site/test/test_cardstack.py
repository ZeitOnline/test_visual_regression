# -*- coding: utf-8 -*-
import pytest
import re


@pytest.mark.parametrize('url', ['/index', '/zeit-online/article/cardstack'])
def test_cardstack_should_be_included_in_content_objects(
        testbrowser, url):
    browser = testbrowser(url)

    # Too bad. We cannot select namespaces elements on undeclared namespaces.
    # This is why we can't use cssselect.
    esihead = ('<esi:include src="http://www.zeit.de'
               '/cardstack-backend/stacks/esi/head')

    assert esihead in browser.contents

    esiscripts = ('<esi:include src="http://www.zeit.de'
                  '/cardstack-backend/stacks/esi/scripts')

    assert esiscripts in browser.contents

    esibody = ('<esi:include src="http://www.zeit.de'
               '/cardstack-backend/stacks/kekse')

    assert esibody in browser.contents


def test_cardstack_should_have_static_param_on_cps(
        testbrowser):
    url = '/index'
    browser = testbrowser(url)

    esihead = ('<esi:include src="http://www.zeit.de'
               '/cardstack-backend/stacks/esi/head.*static=true')

    assert re.search(esihead, browser.contents)


def test_cardstack_should_not_have_static_param_on_articles(testbrowser):
    url = '/zeit-online/article/cardstack'
    browser = testbrowser(url)

    esihead = ('<esi:include src="http://www.zeit.de'
               '/cardstack-backend/stacks/esi/head.*static=true')

    assert not re.search(esihead, browser.contents)
