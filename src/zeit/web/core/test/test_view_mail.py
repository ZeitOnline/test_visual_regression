import zope.component

import zeit.web.core.interfaces


def test_post_should_trigger_mail_then_render_content_again(testbrowser):
    b = testbrowser('/zeit-online/article/feedback')
    b.getControl(name='subject').displayValue = ['Apps']
    b.getControl(name='body').value = 'Emailbody'
    b.getForm(index=1).submit()  # 0=searchform

    mail = zope.component.getUtility(zeit.web.core.interfaces.IMail)
    mail.send.assert_called_with('', 'test@example.com', 'Apps', 'Emailbody')

    assert 'Haben Sie Feedback?' in b.contents
    assert 'Ihr Feedback wurde versendet' in b.contents
