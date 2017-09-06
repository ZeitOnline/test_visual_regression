import zeit.web
import zeit.web.core.centerpage


@zeit.web.register_module('podcast')
class Podcast(zeit.web.core.centerpage.Module,
              zeit.web.core.block.Podcast):
    pass
