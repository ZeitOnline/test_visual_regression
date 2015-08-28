# -*- coding: utf-8 -*-

def test_cardstack_should_be_included_in_cp(
        testbrowser, testserver):
    browser = testbrowser(
        '%s/index' % testserver.url)

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
