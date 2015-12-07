# -*- coding: utf-8 -*-
import re

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
import lxml.etree
import lxml.html
import mock
import pyramid.httpexceptions
import pyramid.testing
import pytest
import requests
import zope.component

import zeit.content.cp.centerpage

import zeit.web.core.centerpage
import zeit.web.core.interfaces
import zeit.web.core.utils
import zeit.web.site.module.playlist
import zeit.web.site.view_centerpage


def test_author_header_should_be_fully_rendered(testserver, testbrowser):
    browser = testbrowser('/autoren/j_random')
    header = browser.cssselect('.author-header')
    name = browser.cssselect('.author-header-info__name')
    summary = browser.cssselect('.author-header-info__summary')
    image = browser.cssselect('.author-header__image')

    assert len(name) == 1
    assert len(summary) == 1
    assert len(image) == 1
