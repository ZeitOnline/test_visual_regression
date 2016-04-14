# -*- coding: utf-8 -*-

import zeit.cms.interfaces
import zeit.web.core.interfaces


def test_campus_centerpage_should_produce_regular_topiclinks(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/centerpage/index')
    topiclink = zeit.web.core.interfaces.ITopicLink(context)
    labels = sorted(dict(topiclink).keys())
    assert labels == ['Ausdauersport', 'Bayerische Landesbank', 'Paul Auster']


def test_campus_article_should_import_topiclinks(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/article/simple')
    topiclink = zeit.web.core.interfaces.ITopicLink(context)
    labels = sorted(dict(topiclink).keys())
    assert labels == ['Ausdauersport', 'Bayerische Landesbank', 'Paul Auster']


def test_campus_article_should_use_default_topiclinks_of_hp(application):
    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/article/simple')
    article_topiclink = zeit.web.core.interfaces.ITopicLink(context)

    context = zeit.cms.interfaces.ICMSContent(
        'http://xml.zeit.de/campus/index')
    hp_topiclink = zeit.web.core.interfaces.ITopicLink(context)

    assert article_topiclink == hp_topiclink


def test_follow_us_has_correct_source(testbrowser):
    select = testbrowser('/campus/centerpage/teaser-follow-us').cssselect
    kicker = select('.teaser-follow-us__packshot .packshot__kicker')
    title = select('.teaser-follow-us__packshot .packshot__title')
    cta = select('.teaser-follow-us__packshot .packshot__cta')
    img = select('.packshot__media > noscript')

    # assert packshot
    assert kicker[0].text == 'Das aktuelle Heft /'
    assert title[0].text == 'ZEIT CAMPUS 1/2016'
    assert 'Jetzt bestellen' in cta[0].text_content()
    assert 'portrait' in img[0].attrib['data-src']

    # check presence of the rest
    assert len(select('.abo-cta')) == 1
    assert len(select('.follow-us')) == 1


def test_module_markup_considers_alignment(testbrowser):
    browser = testbrowser('/campus/centerpage/thema')
    modules = browser.cssselect('.markup')
    for module in modules:
        assert 'markup--center' in module.get('class')
