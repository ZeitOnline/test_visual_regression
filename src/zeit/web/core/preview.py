import pyramid.events
import zeit.frontend.application
import zope.component
import zope.processlifetime


class Application(zeit.frontend.application.Application):

    DONT_SCAN = ['.testing', '.test']

    def configure_zca(self):
        # ZCA setup is done by preview.zcml, which is included by the CMS
        # site.zcml at the right time, so the setup_zodb handler below works.
        pass

    def configure_product_config(self):
        # Since we're running inside the CMS process, the product config is
        # already set up.
        pass

factory = Application()


@zope.component.adapter(zope.processlifetime.IDatabaseOpenedWithRoot)
def setup_zodb(event):
    factory.db = event.database


@pyramid.events.subscriber(pyramid.events.NewRequest)
def set_site(event):
    connection = factory.db.open()
    root = connection.root()
    # We should not hardcode the name, but use ZopePublication.root_name
    # instead, but since the name is not ever going to be changed, we can
    # safely skip the dependency on zope.app.publication.
    root_folder = root.get('Application', None)
    zope.component.hooks.setSite(root_folder)

    def close_db(request):
        # taken from pyramid_zodbconn
        connection.transaction_manager.abort()
        connection.close()
    event.request.add_finished_callback(close_db)
