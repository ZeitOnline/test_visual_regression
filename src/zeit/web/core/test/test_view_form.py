# -*- coding: utf-8 -*-

import zope.component
import requests_mock
import pytest

import zeit.web.core.interfaces


def test_post_should_trigger_mail_then_render_content_again(testbrowser):
    b = testbrowser('/zeit-online/article/feedback')
    b.getControl(name='subject').displayValue = ['Apps']
    b.getControl(name='body').value = 'Emailbody'
    b.getForm(index=1).submit()  # 0=searchform

    mail = zope.component.getUtility(zeit.web.core.interfaces.IMail)
    mail.send.assert_called_with(
        '', 'test@example.com', 'Apps', 'Emailbody\n\n-- \nGesendet von '
        'http://localhost/zeit-online/article/feedback')

    assert 'Williams wackelt weiter' in b.contents
    assert 'Ihr Feedback wurde versendet' in b.contents
    assert 'Ich habe Feedback zum Thema' not in b.contents


def test_missing_captcha_should_render_error_and_preserve_body(
        testbrowser, request):
    captcha = zope.component.getUtility(zeit.web.core.interfaces.ICaptcha)
    captcha.verify.return_value = False

    def reset_mock_captcha():
        captcha.verify.return_value = True
    request.addfinalizer(reset_mock_captcha)

    b = testbrowser('/zeit-online/article/feedback')
    b.getControl(name='subject').displayValue = ['Apps']
    b.getControl(name='body').value = 'Emailbody'
    b.getForm(index=1).submit()  # 0=searchform

    assert 'Sie haben das Captcha' in b.contents
    assert b.getControl(name='body').value == 'Emailbody'


def add_inputs_and_submit(testbrowser):
    b = testbrowser('/zeit-online/article/scrabble-puzzle')
    inputs = {'solution': 'solution',
              'episode': '1',
              'first_name': 'Me',
              'name': 'Myself',
              'e_mail': 'some_mail',
              'street': 'foo',
              'zipcode': '111',
              'city': 'München',
              'phone': '123',
              'coordinates': 'A1-19',
              'points': '34'}
    for name, value in inputs.iteritems():
        b.getControl(name=name).value = value
    b.getForm(index=1).submit()
    return b


def test_puzzle_form_special_input_fields_are_rendered_for_scrabble(
        testbrowser):
    b = testbrowser('/zeit-online/article/scrabble-puzzle')
    assert b.getControl(name='episode')
    assert b.getControl(name='points')
    assert b.getControl(name='coordinates')


def test_puzzle_form_only_standard_input_fields_are_rendered(testbrowser):
    b = testbrowser('/zeit-online/article/winter-puzzle')
    assert b.getControl(name='name')
    with pytest.raises(LookupError):
        assert b.getControl(name='points')
    with pytest.raises(LookupError):
        assert b.getControl(name='episode')


def test_puzzle_form_posts_data_to_backend_and_renders_content_again(
        testbrowser):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    backend_url = conf.get('puzzle_backend')
    with requests_mock.Mocker() as m:
        m.post(backend_url, status_code=201)
        b = add_inputs_and_submit(testbrowser)
        assert m.called
        assert 'Vielen Dank f\xc3\xbcr ihre Einsendung' in b.contents
        assert 'Und das sind diese Woche unsere Preise' in b.contents


def test_puzzle_form_renders_error_message_if_post_fails(
        testbrowser):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    backend_url = conf.get('puzzle_backend')
    with requests_mock.Mocker(real_http=True) as m:
        m.post(backend_url, status_code=500)
        b = add_inputs_and_submit(testbrowser)
        assert m.called
        assert 'Vielen Dank f\xc3\xbcr ihre Einsendung' not in b.contents
        assert 'Leider ist ein technisches Problem aufgetreten' in b.contents
        assert 'Und das sind diese Woche unsere Preise' in b.contents


def test_puzzle_form_sends_correct_json_to_backend(testbrowser):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    backend_url = conf.get('puzzle_backend')
    with requests_mock.Mocker() as m:
        # PostgREST returns a 201 for a successful post
        m.post(backend_url, status_code=201)
        add_inputs_and_submit(testbrowser)
        request = m.last_request
        json_send = request.json()
        assert json_send.get('name') == 'Myself'
        assert json_send.get('country') == 'Deutschland'
        assert json_send.get('type') == 'scrabble'
        assert json_send.get('city') == u'M\xfcnchen'
        assert json_send.get('agreement') is False
