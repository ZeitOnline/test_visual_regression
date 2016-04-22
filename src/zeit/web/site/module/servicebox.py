import zeit.web
import zeit.web.core.module.servicebox


@zeit.web.register_module('servicebox')
class Servicebox(zeit.web.core.module.servicebox.Servicebox):

    source = zeit.web.core.module.servicebox.ServiceSource(
        'servicebox-source')
    title = 'Service'
