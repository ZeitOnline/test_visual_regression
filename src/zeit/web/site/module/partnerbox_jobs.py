import zeit.web
import zeit.web.core.module.jobbox_dropdown


@zeit.web.register_module('partnerbox_jobs')
class PartnerboxJobs(zeit.web.core.module.jobbox_dropdown.JobboxDropdown):

    source = zeit.web.core.module.jobbox_dropdown.JobboxDropdownSource(
        'jobbox-dropdown-source')
    title = 'Partnerbox Jobs'
