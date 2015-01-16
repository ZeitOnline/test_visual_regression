import logging

import pyramid.view

import zeit.content.article.article

import zeit.web.core.security
import zeit.web.core.view


log = logging.getLogger(__name__)


@pyramid.view.view_config(
    route_name='beta_toggle',
    renderer='templates/beta.html')
class Beta(zeit.web.core.view.Base):

    def __call__(self):
        beta = self.request.POST.get('opt')
        if beta in ('in', 'out'):
            beta = 'beta-opt_{}'.format(beta)
        elif self.beta_user:
            beta = 'beta-opt_in'
        if beta:
            self.request.session.update({'site_version': beta})
            return {'site-version': beta}
        return {}

    def __init__(self, context, request):
        self.context = zeit.content.article.article.Article()
        self.request = request

    @property
    def community_user(self):
        return zeit.web.core.security.get_community_user_info(self.request)

    @property
    def beta_user(self):
        return 'beta' in self.community_user.get('roles')

    @property
    def site_version(self):
        version = self.request.session.get('site-version')

        if version in ('beta-opt_in', 'beta-opt_out'):
            return version.lstrip('beta-')

    @property
    def community_host(self):
        return self.request.registry.settings.get('community_host')

    @property
    def friedbert_host(self):
        return self.request.route_url('home')
