# -*- coding: utf-8 -*-
import pytest


@pytest.mark.parametrize('url', ['/index', '/zeit-online/article/01'])
def test_cardstack_should_be_included_in_content_objects(
        testbrowser, url):
    browser = testbrowser(url)

    # To bad. We cannot select namespaces elements on undeclared namespaces.
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
