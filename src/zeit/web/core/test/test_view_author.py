# -*- coding: utf-8 -*-


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
