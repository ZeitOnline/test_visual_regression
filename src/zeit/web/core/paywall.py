import re  # wb
import grokcore
import werkzeug.http
import zope.component

import zeit.web


class Paywall(object):

    @staticmethod
    def c1requestheader_or_get(request, name):
        if name in request.headers:
            return request.headers.get(name, None)
        # We want to allow manipulation via GET-Params for testing,
        # but not in production
        if zeit.web.core.view.is_not_in_production(None, request):
            return request.GET.get(name, None)

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


@grokcore.component.implementer(zeit.web.core.interfaces.IPaywallAccess)
@grokcore.component.adapter(zeit.cms.content.interfaces.ICommonMetadata)
def access_for_common_content(context):
    return context.access


@grokcore.component.implementer(zeit.web.core.interfaces.IPaywallAccess)
@grokcore.component.adapter(zeit.content.cp.interfaces.ICP2015)
def access_for_cps(context):
    if context.type == 'volume':
            volume = zeit.content.volume.interfaces.IVolume(context, None)

            # When we have a volume and there is no next volume,
            # it is considered to be the newest volume.
            if volume is not None and volume.next is None:
                return 'abo'
    return context.access


class CeleraOneMixin(object):

    def __call__(self):
        resp = super(CeleraOneMixin, self).__call__()
        self.request.response.headers.update(self.c1_header)
        self.set_c1_meter_response_headers()
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
        pattern = r'[^ %s]' % ''.join(werkzeug.http._token_chars)
        return re.sub(pattern, '', string.encode('utf-8', 'ignore'))

    def _get_c1_heading(self, prep=unicode):
        if getattr(self.context, 'title', None) is not None:
            return prep(self.context.title.strip())

    def _get_c1_kicker(self, prep=unicode):
        if getattr(self.context, 'supertitle', None) is not None:
            return prep(self.context.supertitle.strip())

    @zeit.web.reify
    def c1_client(self):
        return [(k, u'"{}"'.format(v.replace('"', r'\"'))) for k, v in {
            'set_channel': self._c1_channel,
            'set_sub_channel': self._c1_sub_channel,
            'set_cms_id': self._c1_cms_id,
            'set_content_id': self._c1_content_id,
            'set_doc_type': self._c1_doc_type,
            'set_entitlement': self._c1_entitlement,
            'set_heading': self._get_c1_heading(),
            'set_kicker': self._get_c1_kicker(),
            'set_service_id': 'zon'
        }.items() if v is not None] + [
            ('set_origin', 'window.Zeit.getCeleraOneOrigin()')]

    @zeit.web.reify
    def c1_header(self):
        return [(k, v.encode('utf-8', 'ignore')) for k, v in {
            'C1-Track-Channel': self._c1_channel,
            'C1-Track-Sub-Channel': self._c1_sub_channel,
            'C1-Track-CMS-ID': self._c1_cms_id,
            'C1-Track-Content-ID': self._c1_content_id,
            'C1-Track-Doc-Type': self._c1_doc_type,
            'C1-Track-Entitlement': self._c1_entitlement,
            'C1-Track-Heading': self._get_c1_heading(self._headersafe),
            'C1-Track-Kicker': self._get_c1_kicker(self._headersafe),
            'C1-Track-Service-ID': 'zon'
        }.items() if v is not None]

    def set_c1_meter_response_headers(self):

        conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
        if conf.get('environment') == 'production':
            return

        request = self.request

        for req_header_name in request.headers:
            if req_header_name.startswith('C1-Meter-'):
                res_header_name = 'X-Debug-{}'.format(req_header_name)
                res_header_value = request.headers.get(req_header_name, '')
                request.response.headers[res_header_name] = res_header_value
