import re  # wb
import grokcore
import zope.component

import zeit.web


class Paywall(object):

    @staticmethod
    def c1requestheader_or_get(request, name):
        # We want to allow manipulation via GET-Params for testing,
        # but not in production
        if zeit.web.core.view.is_not_in_production(None, request):
            if request.GET.get(name, None):
                return request.GET.get(name, None)

        if name in request.headers:
            return request.headers.get(name, None)

    @staticmethod
    def status(request):
        """See https://github.com/ZeitOnline/zeit.web/wiki/CeleraOne-Schranken
        for possible headers and their meaning.
        """
        if not zeit.web.core.application.FEATURE_TOGGLES.find(
                'reader_revenue'):
            return False

        c1_meter_status = Paywall.c1requestheader_or_get(
            request, 'C1-Meter-Status')
        c1_meter_user_status = Paywall.c1requestheader_or_get(
            request, 'C1-Meter-User-Status')

        if not c1_meter_status:
            return None
        else:
            if c1_meter_status == 'always_paid':
                return 'paid'
            elif c1_meter_status == 'paywall':
                # "metered" is deduced indirectly:
                # To avoid metered-counts (would bloat varnish buckets),
                # we check the user status when "paywall" occurs.
                if c1_meter_user_status == 'anonymous':
                    return 'register'
                else:
                    return 'metered'
            else:
                # In doubt, if C1 sends something unexpected,
                # we show the content.
                return None

        return None

    @staticmethod
    def first_click_free(request):
        if not zeit.web.core.application.FEATURE_TOGGLES.find(
                'reader_revenue'):
            return False

        c1_meter_status = Paywall.c1requestheader_or_get(
            request, 'C1-Meter-Status')
        c1_meter_info = Paywall.c1requestheader_or_get(
            request, 'C1-Meter-Info')

        return (
            c1_meter_status == 'open' and c1_meter_info == 'first_click_free')


@grokcore.component.implementer(zeit.web.core.interfaces.IPaywallAccess)
@grokcore.component.adapter(zeit.cms.content.interfaces.ICommonMetadata)
def access_for_common_content(context):
    return context.access


@grokcore.component.implementer(zeit.web.core.interfaces.IPaywallAccess)
@grokcore.component.adapter(zeit.content.cp.interfaces.ICenterPage)
def access_for_cps(context):
    if context.type == 'volume':
            volume = zeit.content.volume.interfaces.IVolume(context, None)

            # When we have a volume and there is no next volume,
            # it is considered to be the newest volume.
            if volume is not None and volume.next is None:
                return 'abo'
    return context.access


# According to <https://tools.ietf.org/html/rfc7230#section-3.2>
# HTTP header values may consist of VCHAR, visible ASCII characters. However,
# our titles and such of course contain spaces (which strictly count as
# "invisible"), so we allow it, since it does not seem to cause any trouble in
# our stack.
ASCII_INVISIBLE_CHARACTERS = ''.join([chr(x) for x in range(32)] + [chr(127)])


class CeleraOneMixin(object):

    def __call__(self):
        resp = super(CeleraOneMixin, self).__call__()
        self.request.response.headers.update(self.c1_header)
        self.set_c1_meter_response_headers()
        self.set_c1_adblocker_response_headers()
        return resp

    @zeit.web.reify
    def _c1_channel(self):
        return getattr(self, 'ressort', None)

    @zeit.web.reify
    def _c1_sub_channel(self):
        return getattr(self, 'sub_ressort', None)

    @zeit.web.reify
    def _c1_entitlement(self):
        access = zeit.web.core.interfaces.IPaywallAccess(self.context)
        access_source = zeit.cms.content.sources.ACCESS_SOURCE.factory
        return access_source.translate_to_c1(access)

    @zeit.web.reify
    def _c1_entitlement_id(self):
        return None if (
            self._c1_entitlement == 'free' or self._c1_entitlement is None
        ) else 'zeit-fullaccess'

    @zeit.web.reify
    def _c1_cms_id(self):
        uuid = zeit.cms.content.interfaces.IUUID(self.context, None)
        return getattr(uuid, 'id', None)

    @zeit.web.reify
    def _c1_content_id(self):
        return self.webtrekk_content_id

    @zeit.web.reify
    def _c1_doc_type(self):
        if self.type == 'gallery':
            return 'bildergalerie'
        elif isinstance(self, zeit.web.core.view.FrameBuilder):
            return 'arena'
        else:
            return self.type

    @classmethod
    def _headersafe(cls, string):
        pattern = r'[%s]' % ASCII_INVISIBLE_CHARACTERS
        return re.sub(pattern, '', string.encode('ascii', 'ignore'))

    def _get_c1_heading(self):
        if getattr(self.context, 'title', None) is not None:
            return self.context.title.strip()

    def _get_c1_kicker(self):
        if getattr(self.context, 'supertitle', None) is not None:
            return self.context.supertitle.strip()

    @zeit.web.reify
    def c1_client(self):
        return [(k, u'"{}"'.format(v.replace('"', r'\"'))) for k, v in {
            'set_channel': self._c1_channel,
            'set_sub_channel': self._c1_sub_channel,
            'set_cms_id': self._c1_cms_id,
            'set_content_id': self._c1_content_id,
            'set_doc_type': self._c1_doc_type,
            'set_entitlement': self._c1_entitlement,
            'set_entitlement_id': self._c1_entitlement_id,
            'set_heading': self._get_c1_heading(),
            'set_kicker': self._get_c1_kicker(),
            'set_service_id': 'zon'
        }.items() if v is not None] + [
            ('set_origin', 'window.Zeit.getCeleraOneOrigin()')]

    @zeit.web.reify
    def c1_header(self):
        return [(k, self._headersafe(v)) for k, v in {
            'C1-Track-Channel': self._c1_channel,
            'C1-Track-Sub-Channel': self._c1_sub_channel,
            'C1-Track-CMS-ID': self._c1_cms_id,
            'C1-Track-Content-ID': self._c1_content_id,
            'C1-Track-Doc-Type': self._c1_doc_type,
            'C1-Track-Entitlement': self._c1_entitlement,
            'C1-Track-Entitlement-ID': self._c1_entitlement_id,
            'C1-Track-Heading': self._get_c1_heading(),
            'C1-Track-Kicker': self._get_c1_kicker(),
            'C1-Track-Service-ID': 'zon'
        }.items() if v is not None]

    def set_c1_meter_response_headers(self):

        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        if conf.get('environment') == 'production':
            return

        request = self.request

        headers = {}
        headers.update(request.headers)
        headers.update(request.response.headers)

        # Since C1 strips our C1-Track-* Headers, but we want to see them,
        # we "copy" them into X-Debug-Headers.
        # And: we also want to echo the C1-Meter Headers comming from them
        # on the 2nd round trip.
        for name in headers:
            if name.startswith('C1-'):
                res_name = 'X-Debug-{}'.format(name)
                value = headers.get(name, '')
                request.response.headers[res_name] = value

    def set_c1_adblocker_response_headers(self):
        if zeit.web.core.application.FEATURE_TOGGLES.find(
                'c1_adblocker_blocker'):

            # First test implementation with two hardcoded articles.
            # Logic will follow.
            response = self.request.response
            if self.context.uniqueId == 'http://xml.zeit.de/digital/' \
                    'internet/2017-11/firefox-quantum-browser-test-' \
                    'vergleich-google-chrome':
                response.headers['C1-Track-Adblocker-Targeting'] = 'false'
                return True
            if self.context.uniqueId == 'http://xml.zeit.de/digital/' \
                    'internet/2018-04/adblocker-urteil-bgh-springer-' \
                    'adblock-plus':
                response.headers['C1-Track-Adblocker-Targeting'] = 'true'
                return True
