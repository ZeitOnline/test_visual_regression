from cornice.service import Service
from pyramid.security import authenticated_userid
from pyramid.settings import asbool

from .security import ZMO_USER_KEY


def assemble_app_info(request):
    settings = request.registry.settings
    result = dict(debug=asbool(settings.get('debug', False)))
    userid = authenticated_userid(request)
    if userid:
        result['authenticated'] = True
    else:
        result['authenticated'] = False
    result['user'] = request.session.get(ZMO_USER_KEY, dict())
    return dict(result)


app_info = Service(name='appinfo', path='/-/', renderer='json', accept='application/json')


@app_info.get()
def get_app_info(request):
    return request.app_info