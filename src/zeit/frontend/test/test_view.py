import mock
from zeit.frontend import view


def test_breadcumb_should_produce_expected_data():
    context = mock.Mock()
    context.ressort = 'zmo'
    context.sub_ressort = 'lebensart'
    context.title = 'This is my title'

    view._navigation = {
        'start': ('Start', 'http://www.zeit.de/index', 'myid1'),
        'zmo': ('ZEIT Magazin', 'http://www.zeit.de/magazin/index', 'myid2'),
        'lebensart': ('ZEIT Magazin',
                      'http://www.zeit.de/magazin/lebensart/index',
                      'myid3'), }

    article = view.Article(context, '')

    l = [
        ('Start', 'http://www.zeit.de/index', 'myid1'),
        ('ZEIT Magazin', 'http://www.zeit.de/magazin/index', 'myid2'),
        ('ZEIT Magazin', 'http://www.zeit.de/magazin/lebensart/index',
            'myid3'),
        ('This is my title', 'http://localhost'), ]

    assert article.breadcrumb == l


def test_breadcrumb_should_be_shorter_if_ressort_or_sub_ressort_is_unknown():
    context = mock.Mock()
    context.ressort = 'zmx'
    context.sub_ressort = 'lebensart'
    context.title = 'This is my title'

    view._navigation = {
        'start': ('Start', 'http://www.zeit.de/index', 'myid1'),
        'zmo': ('ZEIT Magazin', 'http://www.zeit.de/magazin/index', 'myid2'),
        'lebensart': ('ZEIT Magazin',
                      'http://www.zeit.de/magazin/lebensart/index',
                      'myid3'), }

    article = view.Article(context, '')

    l = [
        ('Start', 'http://www.zeit.de/index', 'myid1'),
        ('ZEIT Magazin', 'http://www.zeit.de/magazin/lebensart/index',
            'myid3'),
        ('This is my title', 'http://localhost'), ]

    assert article.breadcrumb == l
