from cornice.service import Service
from pyramid.security import authenticated_userid
from pyramid.settings import asbool

from .security import ZMO_USER_KEY
app_info = Service(name='appinfo', path='/-/', renderer='json', accept='application/json')


@app_info.get()
def get_app_info(request):
    settings = request.registry.settings
    result = dict(debug=asbool(settings.get('debug', False)))
    userid = authenticated_userid(request)
    if userid:
        result['authenticated'] = True
    else:
        result['authenticated'] = False
    # TODO: should expose the user info as custom request predicate
    # instead of exposing the session key here
    return dict(result, **request.session[ZMO_USER_KEY])
