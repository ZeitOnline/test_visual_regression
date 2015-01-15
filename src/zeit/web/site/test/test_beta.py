import pytest


@pytest.mark.parametrize('selector,cookies', [
    ('.beta-teaser', {}),
    ('.beta-teaser', {'site-version': 'foo'}),
    ('.beta-toggle', {'site-version': 'opt_in'}),
    ('.beta-toggle', {'site-version': 'opt_out'})
])
def test_beta_view_should_display_info_text_if_missing_cookie(
        selector, cookies, testbrowser, testserver):
    browser = testbrowser('%s/beta' % testserver.url)
    browser.cookies.update(cookies)
    browser.reload()
    assert len(browser.cssselect(selector)) == 1
    browser.cookies.clear()


@pytest.mark.parametrize('cookies,opt_in,opt_out', [
    ({'site-version': 'opt_in'}, 1, 0),
    ({'site-version': 'opt_out'}, 0, 1)
])
def test_beta_view_should_correctly_display_toggled_toggle(
        cookies, opt_in, opt_out, testbrowser, testserver):
    browser = testbrowser('%s/beta' % testserver.url)
    browser.cookies.update(cookies)
    browser.reload()
    toggle = browser.cssselect('.beta-toggle__cta')[0]
    assert len(toggle.cssselect('input[value="opt_in"][checked]')) == opt_in
    assert len(toggle.cssselect('input[value="opt_out"][checked]')) == opt_out


@pytest.mark.parametrize('payload,cookies', [
    ({'beta': 'opt_in'}, {'site-version': 'beta-opt_in'}),
    ({'beta': 'opt_out'}, {'site-version': 'beta-opt_out'})
])
def test_beta_view_should_correctly_update_cookie_on_post(
        payload, cookies, testbrowser, testserver):
    browser = testbrowser('%s/beta' % testserver.url)
    browser.cookies.update(cookies)
    browser.open('%s/beta' % testserver.url, data=payload)
    __import__('pdb').set_trace()
