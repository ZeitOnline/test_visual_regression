import logging

import zeit.web
import zeit.web.site.module


log = logging.getLogger(__name__)


@zeit.web.register_module('partnerbox_jobs')
class PartnerJobs(zeit.web.site.module.Module, list):

    pass
