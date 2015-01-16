import pytest
import requests


@pytest.mark.parametrize('selector,cookies', [
    ('.beta-prompt', {}),
    ('.beta-prompt', {'site-version': 'foo'}),
    ('.beta-toggle', {'site-version': 'opt_in'}),
    ('.beta-toggle', {'site-version': 'opt_out'})
])
def test_beta_view_should_display_info_text_if_missing_cookie(
        selector, cookies, css_selector, testserver):
    resp = requests.get('{}/beta'.format(testserver.url),
                        cookies=cookies)
    __import__('pdb').set_trace()
    assert css_selector(selector, resp.content) == 1


@pytest.mark.parametrize('cookies,opt_in,opt_out', [
    ({'site-version': 'opt_in'}, 1, 0),
    ({'site-version': 'opt_out'}, 0, 1)
])
def test_beta_view_should_correctly_display_toggled_toggle(
        cookies, opt_in, opt_out, css_selector, testserver):
    resp = requests.get('{}/beta'.format(testserver.url),
                        cookies=cookies)
    toggle = css_selector('.beta-toggle__cta', resp.content)[0]
    assert len(toggle.cssselect('input[value="opt_in"][checked]')) == opt_in
    assert len(toggle.cssselect('input[value="opt_out"][checked]')) == opt_out


@pytest.mark.parametrize('payload,cookies', [
    ({'beta': 'opt_in'}, {'site-version': 'beta-opt_in'}),
    ({'beta': 'opt_out'}, {'site-version': 'beta-opt_out'})
])
def test_beta_view_should_correctly_update_cookie_on_post(
        payload, cookies, css_selector, testserver):
    resp = requests.get('{}/beta'.format(testserver.url),
                        data=payload, cookies=cookies)
    assert css_selector('a', resp.content)
