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
