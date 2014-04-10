# -*- coding: utf-8 -*-
import datetime


def test_entry_for_linkreach_should_deserialize():
    from zeit.frontend.reach import _Entry
    from zeit.frontend.reach import Entry

    data = {
        'score': 1235,
        'location': '/foo',
        'supertitle': 'my_supertitle',
        'title': 'my_title',
        'subtitle': 'my_subtitle',
        'timestamp': 1397127353368,
        'section': 'my_section',
        'fetched_at': 1397127353368,
    }

    schema = _Entry()
    person = Entry(schema.deserialize(data))

    assert person.score == 1235
    assert person.location == '/foo'
    assert person.title == 'my_title'
    assert person.subtitle == 'my_subtitle'
    assert person.supertitle == 'my_supertitle'
    assert person.section == 'my_section'

    my_date = datetime.datetime(2014, 4, 10, 12, 55, 53)
    assert person.fetched_at.replace(tzinfo=None) == my_date
    assert person.timestamp.replace(tzinfo=None) == my_date
