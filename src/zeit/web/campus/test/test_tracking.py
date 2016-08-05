# -*- coding: utf-8 -*-


def test_campus_meetrics_is_present_on_hp(testbrowser):
    browser = testbrowser('/campus/index')
    assert len(browser.cssselect(
        'script[src="//s62.mxcdn.net/bb-serve/mtrcs_225560.js"]')) == 1
    assert 'try { loadMWA208571(); } catch (e) {}' in browser.contents
    assert 'try { mainMWA208571(); } catch (e) {}' in browser.contents


def test_campus_meetrics_is_not_present_on_cp(testbrowser):
    browser = testbrowser('/campus/centerpage/index')
    assert len(browser.cssselect(
        'script[src="//s62.mxcdn.net/bb-serve/mtrcs_225560.js"]')) == 0
    assert 'loadMWA208571' not in browser.contents
    assert 'mainMWA208571' not in browser.contents


def test_campus_meetrics_is_present_on_article(testbrowser):
    browser = testbrowser('/campus/article/simple')
    assert len(browser.cssselect(
        'script[src="//s62.mxcdn.net/bb-serve/mtrcs_225560.js"]')) == 1
    assert 'try { loadMWA208571(); } catch (e) {}' in browser.contents
    assert 'try { mainMWA208571(); } catch (e) {}' in browser.contents
