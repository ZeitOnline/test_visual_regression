# -*- coding: utf-8 -*-
import zeit.web.core.application


def test_campus_meetrics_is_present_on_hp(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set('third_party_modules')
    browser = testbrowser('/campus/index')
    assert len(browser.cssselect(
        'script[src="//s62.mxcdn.net/bb-serve/mtrcs_225560.js"]')) == 1
    assert 'try { loadMWA208571(); } catch (e) {}' in browser.contents
    assert 'try { mainMWA208571(); } catch (e) {}' in browser.contents


def test_campus_meetrics_is_present_on_cp(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set('third_party_modules')
    browser = testbrowser('/campus/centerpage/index')
    assert len(browser.cssselect(
        'script[src="//s62.mxcdn.net/bb-serve/mtrcs_225560.js"]')) == 1
    assert 'try { loadMWA208571(); } catch (e) {}' in browser.contents
    assert 'try { mainMWA208571(); } catch (e) {}' in browser.contents


def test_campus_meetrics_is_present_on_article(testbrowser):
    zeit.web.core.application.FEATURE_TOGGLES.set('third_party_modules')
    browser = testbrowser('/campus/article/simple')
    assert len(browser.cssselect(
        'script[src="//s62.mxcdn.net/bb-serve/mtrcs_225560.js"]')) == 1
    assert 'try { loadMWA208571(); } catch (e) {}' in browser.contents
    assert 'try { mainMWA208571(); } catch (e) {}' in browser.contents
