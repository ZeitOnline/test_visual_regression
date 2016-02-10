import zeit.web.core.view


def is_zco_content(context, request):
    # XXX This is a mocked predicate until we have a zeit.campus interface
    return context.uniqueId == 'http://xml.zeit.de/campus/index'


class Base(zeit.web.core.view.Base):
    pass
