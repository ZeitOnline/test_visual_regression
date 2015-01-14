import logging

import pyramid.view

import zeit.content.article.article

import zeit.web.core.view


log = logging.getLogger(__name__)


@pyramid.view.view_config(
    route_name='beta_toggle',
    renderer='templates/beta.html')
class Beta(zeit.web.core.view.Base):

    def __call__(self):
        return {}

    def __init__(self, context, request):
        self.context = zeit.content.article.article.Article()
        self.request = request

    @property
    def beta_version(self):
        return 'site-version' in self.request.session

    @property
    def opted_in(self):
        site_version = self.request.session.get('site-version')

        if site_version not in ('beta-opt_in', 'beta-opt_out'):
            return
        else:
            return 'opt_in' in site_version
