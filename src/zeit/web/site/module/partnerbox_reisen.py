import logging

import zeit.web
import zeit.web.core.centerpage


log = logging.getLogger(__name__)


@zeit.web.register_module('partnerbox_reisen')
class PartnerJobs(zeit.web.core.centerpage.Module, list):

    pass
