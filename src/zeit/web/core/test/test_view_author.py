# -*- coding: utf-8 -*-

import zope.component

import zeit.web.core.interfaces

def test_author_page_should_render_bio_questions(testbrowser):
    browser = testbrowser('/autoren/D/Tobias_Dorfer')
    question1 = browser.cssselect('.author-questions__title')[0].text
    question2 = browser.cssselect('.author-questions__title')[1].text
    question3 = browser.cssselect('.author-questions__title')[2].text
    question4 = browser.cssselect('.author-questions__title')[3].text
    question5 = browser.cssselect('.author-questions__title')[4].text
    question6 = browser.cssselect('.author-questions__title')[5].text
    question7 = browser.cssselect('.author-questions__title')[6].text
    question8 = browser.cssselect('.author-questions__title')[7].text
    assert question1 == 'Transparenzhinweis'
    assert question2 == 'Das treibt mich an'
    assert question3 == 'Da komme ich her'
    assert question4 == u'Dieses Ereignis hat mich journalistisch geprägt'
    assert question5 == 'Diesem Thema widme ich die meiste Zeit'
    assert question6 == 'Das mache ich jenseits von meiner Arbeit'
    assert question7 == ('Mit diesem Menschen hatte ich als Journalist einen '
                         'unvergesslichen Moment')
    assert question8 == u'Diese Recherche hat etwas verändert'

def test_author_has_contact_link(testbrowser):
    browser = testbrowser('/autoren/D/Tobias_Dorfer/index/feedback')

    # has contact link
    feedbackLinkArray = browser.cssselect('.author-contact__link')
    hasFeedbackLink = False
    for feedbackLink in feedbackLinkArray:
        if feedbackLink.attrib.get('href').endswith(
            'autoren/D/Tobias_Dorfer/index/feedback#author-content'):
            hasFeedbackLink = True

    assert hasFeedbackLink

def test_author_page_should_render_feedback(testbrowser):
    browser = testbrowser('/autoren/D/Tobias_Dorfer/index/feedback')

    # has feedback section
    feedbackBox = browser.cssselect('.feedback-section')
    assert len(feedbackBox) == 1

    # has section intro text
    feedbackIntro = browser.cssselect('.feedback-form__inner p')[0].text
    assert feedbackIntro.startswith('Ihr Feedback an')

    # has required textarea
    feedbackTextarea = browser.cssselect('.feedback-form__textarea')[0]
    assert feedbackTextarea.attrib.has_key('required')

def test_post_should_trigger_mail_then_render_success(testbrowser):
    # load thomas to make sure no real author gets test mails
    b = testbrowser('/autoren/S/Thomas_Strothjohann/index/feedback')

    b.getControl(name='body').value = 'Testfeedback body'
    # submit form
    b.getForm(name='feedbackform').submit()

    mail = zope.component.getUtility(zeit.web.core.interfaces.IMail)
    mail.send.assert_called_with('', 'thomas.strothjohann@zeit.de',
        'Sie haben Feedback erhalten',
        'Testfeedback body\n\n-- \nGesendet von ' +
        'http://localhost/autoren/S/Thomas_Strothjohann/index')

    assert 'Ihr Feedback wurde erfolgreich verschickt.' in b.contents
    assert 'Ihr Feedback an' not in b.contents

def test_author_missing_captcha_should_render_error_and_preserve_body(
        testbrowser, request):
    captcha = zope.component.getUtility(zeit.web.core.interfaces.ICaptcha)
    captcha.verify.return_value = False

    def reset_mock_captcha():
        captcha.verify.return_value = True
    request.addfinalizer(reset_mock_captcha)

    b = testbrowser('/autoren/S/Thomas_Strothjohann/index/feedback')
    b.getControl(name='subject').value = 'Sie haben Feedback erhalten.'
    b.getControl(name='body').value = 'Emailbody'
    b.getForm(name='feedbackform').submit()

    assert 'Sie haben das Captcha' in b.contents
    assert b.getControl(name='body').value == 'Emailbody'
