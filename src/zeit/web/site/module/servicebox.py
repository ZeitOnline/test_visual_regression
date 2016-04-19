import zeit.web
import zeit.web.core.module.servicebox


@zeit.web.register_module('servicebox')
class Servicebox(zeit.web.core.module.servicebox.Servicebox):

    services = zeit.web.core.module.servicebox.ServiceSource(
        'servicebox-source')
    items_per_column = 5
    title = 'Service'
