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
        original = self.request.session.get('site-version')
        update = self.request.POST.get('opt')
        if original in ('beta-opt_in', 'beta-opt_out'):
            original = original.lstrip('beta-')
        if update in ('in', 'out'):
            update = 'opt_{}'.format(update)
        if update is not None and original != update:
            self.request.session.update({'site_version': update})
        return update or original

    @property
    def community_host(self):
        return self.request.registry.settings.get('community_host')

    @property
    def friedbert_host(self):
        return self.request.route_url('home')
