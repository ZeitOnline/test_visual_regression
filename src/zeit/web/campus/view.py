import pyramid.view

import zeit.campus.interfaces

import zeit.web.core.application
import zeit.web.core.security
import zeit.web.core.view


def is_zco_content(context, request):
    toggle = zeit.web.core.application.FEATURE_TOGGLES.find('campus_launch')
    return toggle and zeit.campus.interfaces.IZCOContent.providedBy(context)


class Base(zeit.web.core.view.Base):

    @zeit.web.reify
    def adcontroller_handle(self):
        # TODO: lokale HP von Campus besser erkennen? Haengt die Info auch
        # an der Seite? (Ziel: dass die Tests auch ohne die Hereingabe
        # des path in den DummyRequest funktionieren.)
        if self.type == 'centerpage' and self.request.path == '/campus/index':
            return 'index'
        if self.type == 'centerpage':
            return 'centerpage'
        return 'artikel'

    @zeit.web.reify
    def adcontroller_values(self):
        """Fill the adcontroller js object with actual values.
        Output in level strings only allows latin characters, numbers and
        underscore."""
        keywords = ','.join(self.adwords)
        return [('$handle', self.adcontroller_handle),
                ('level2', 'campus'),
                ('level3', 'TODO'),
                ('level4', 'TODO'),
                ('$autoSizeFrames', True),
                ('keywords', keywords),
                ('tma', '')]


@pyramid.view.view_config(
    route_name='login_state',
    renderer='templates/inc/navigation/login-state.html',
    request_param='for=campus',
    http_cache=60)
def login_state(request):
    return zeit.web.core.security.get_login_state(request)
