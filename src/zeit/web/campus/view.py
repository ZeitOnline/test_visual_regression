import zeit.web.core.application
import zeit.web.core.view


def is_zco_content(context, request):
    # XXX This is a mocked predicate until we have a zeit.campus interface
    toggle = zeit.web.core.application.FEATURE_TOGGLES.find('campus_launch')
    return toggle and context.uniqueId.startswith('http://xml.zeit.de/campus')


class Base(zeit.web.core.view.Base):
    pass
