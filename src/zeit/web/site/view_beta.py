import logging

import pyramid.view


log = logging.getLogger(__name__)


@pyramid.view.view_config(
    route_name='beta_toggle',
    renderer='templates/beta.html')
class Beta(object):

    def __call__(self):
        return {}

    def __init__(self, context, request):
        self.context = context
        self.request = request
