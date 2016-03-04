# coding: utf8
import re

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

        topiclabel = getattr(self.context, 'topicpagelink_label', '')

        # OPTIMIZE: move this into an own function for all views?
        if topiclabel:
            topiclabel = topiclabel.lower().replace(
                u'ä', 'ae').replace(
                u'ö', 'oe').replace(
                u'ü', 'ue').replace(
                u'á', 'a').replace(
                u'à', 'a').replace(
                u'é', 'e').replace(
                u'è', 'e').replace(
                u'ß', 'ss')
            topiclabel = re.sub(u'[^_a-zA-Z0-9]', '_', topiclabel)
            topiclabel = re.sub(u'_+', '_', topiclabel)
            topiclabel = re.sub(u'^_|_$', '', topiclabel)

        return [('$handle', self.adcontroller_handle),
                ('level2', 'campus'),
                ('level3', 'thema' if topiclabel else ''),
                ('level4', topiclabel or ''),
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


@pyramid.view.view_config(
    route_name='campus_framebuilder',
    renderer='templates/framebuilder/framebuilder.html')
class FrameBuilder(zeit.web.core.view.FrameBuilder, Base):

    def __init__(self, context, request):
        super(FrameBuilder, self).__init__(context, request)
        try:
            self.context = zeit.cms.interfaces.ICMSContent(
                'http://xml.zeit.de/campus/index')
            self.context.advertising_enabled = self.banner_on
        except TypeError:
            raise pyramid.httpexceptions.HTTPNotFound()
