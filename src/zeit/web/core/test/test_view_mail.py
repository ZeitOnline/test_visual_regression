import zope.component

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
