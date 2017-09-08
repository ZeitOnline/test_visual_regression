# -*- coding: utf-8 -*-


def test_campus_meetrics_is_present_on_hp(testbrowser, togglepatch):
    togglepatch({'third_party_modules': True})
    browser = testbrowser('/campus/index')
    assert len(browser.cssselect(
        'script[src="//s62.mxcdn.net/bb-serve/mtrcs_225560.js"]')) == 1
    assert 'try { loadMWA208571(); } catch (e) {}' in browser.contents
    assert 'try { mainMWA208571(); } catch (e) {}' in browser.contents


def test_campus_meetrics_is_present_on_cp(testbrowser, togglepatch):
    togglepatch({'third_party_modules': True})
    browser = testbrowser('/campus/centerpage/index')
    assert len(browser.cssselect(
        'script[src="//s62.mxcdn.net/bb-serve/mtrcs_225560.js"]')) == 1
    assert 'try { loadMWA208571(); } catch (e) {}' in browser.contents
    assert 'try { mainMWA208571(); } catch (e) {}' in browser.contents


def test_campus_meetrics_is_present_on_article(testbrowser, togglepatch):
    togglepatch({'third_party_modules': True})
    browser = testbrowser('/campus/article/simple')
    assert len(browser.cssselect(
        'script[src="//s62.mxcdn.net/bb-serve/mtrcs_225560.js"]')) == 1
    assert 'try { loadMWA208571(); } catch (e) {}' in browser.contents
    assert 'try { mainMWA208571(); } catch (e) {}' in browser.contents
