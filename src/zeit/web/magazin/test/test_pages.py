# -*- coding: utf-8 -*-
import socket

import pytest


@pytest.mark.skipif(socket.gethostname != 'buildbert',
                    reason='Aint nobody got time fo dat.')
def test_js_flawless_document_load(selenium_driver, testserver):
    driver = selenium_driver
    for i in range(1, 10):
        driver.get('%s/zeit-magazin/article/%02d' % (testserver.url, i))
        errors = driver.execute_script('return window.jsErrors')
        assert not errors
