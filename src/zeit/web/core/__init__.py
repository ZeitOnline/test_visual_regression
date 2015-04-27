import zope.component
import zeit.web.core.interfaces


__import__('pkg_resources').declare_namespace(__name__)


def is_admin(context, request):
    conf = zope.component.getUtility(zeit.web.core.interfaces.ISettings)
    if conf.get('is_admin'):
        return True
    return request.client_addr == '127.0.0.1'
