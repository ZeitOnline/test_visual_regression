import logging

import pyramid.view
import pyramid.httpexceptions

import zeit.content.article.article

import zeit.web.core.security
import zeit.web.core.view
import zeit.web.core.template


log = logging.getLogger(__name__)


@pyramid.view.view_config(
    route_name='beta_toggle_json',
    renderer='json')
class BetaJSON(zeit.web.core.view.Base):

    def __init__(self, context, request):
        self.context = zeit.content.article.article.Article()
        self.request = request

    def __call__(self):
        self.request.response.cache_expires(0)
        original = self.request.cookies.get('site-version')
        update = self.request.POST.get('opt')
        return {'site-version': self._set_opt_cookie(original, update)}

    def _set_opt_cookie(self, original, update):
        if original in ('beta-opt_in', 'beta-opt_out'):
            original = original.lstrip('beta-')
        if update in ('in', 'out'):
            update = 'opt_{}'.format(update)
        if update is not None and original != update:
            # Users w/o beta role should not be able to toggle th cookie value
            if self.beta_user:
                self.request.response.set_cookie(
                    'site-version',
                    value='beta-%s' % update,
                    max_age=(60 * 60 * 24 * 30)  # cookie lifetime = 30 days
                )
        return update or original

    @property
    def community_user(self):
        return zeit.web.core.security.get_community_user_info(self.request)

    @property
    def beta_user(self):
        return 'beta' in self.community_user.get('roles')

    @property
    def meta_robots(self):
        return 'noindex,nofollow,noarchive'

    @property
    def site_version(self):
        return self._set_opt_cookie(
            self.request.cookies.get('site-version'),
            self.request.params.get('version'))

    @property
    def friedbert_host(self):
        return self.request.route_url('home')

    @property
    def beta_teaser_img(self):
        unique_id = 'http://xml.zeit.de/administratives/beta-teaser.jpg'
        try:
            zeit.cms.interfaces.ICMSContent(unique_id)
        except TypeError:
            return
        return unique_id.replace('http://xml.zeit.de/', self.friedbert_host, 1)


@pyramid.view.view_config(
    route_name='beta_toggle',
    renderer='templates/beta.html')
class Beta(BetaJSON):
    def __call__(self):
        res = super(Beta, self).__call__()
        location = '{}#{}'.format(
            zeit.web.core.template.append_get_params(
                self.request, version=res['site-version']),
            'beta-title')
        if self.request.method == 'POST':
            raise pyramid.httpexceptions.HTTPSeeOther(location=location)
        original = self.request.cookies.get('site-version')
        update = self.request.params.get('version')
        self._set_opt_cookie(original, update)
        return {}
