import zeit.web
import zeit.web.core.module.servicebox


@zeit.web.register_module('zco-servicelinks')
class Servicebox(zeit.web.core.module.servicebox.Servicebox):

    # XXX Could we determine the XML file from the cpextra id, instead of
    # having to explicitly map it?
    services = zeit.web.core.module.servicebox.ServiceSource(
        'zco-servicelinks-source')
    title = 'Mehr Service'
