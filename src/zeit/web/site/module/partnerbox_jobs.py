import logging

import zeit.web
import zeit.web.core.module


log = logging.getLogger(__name__)


@zeit.web.register_module('partnerbox_jobs')
class PartnerJobs(zeit.web.core.module.Module, list):

    pass
