import cornice.service
import pyramid.security
import pyramid.settings


def assemble_app_info(request):
    settings = request.registry.settings
    result = dict(debug=pyramid.settings.asbool(settings.get('debug', False)))
    userid = pyramid.security.authenticated_userid(request)
    if userid:
        result['authenticated'] = True
    else:
        result['authenticated'] = False
    result['user'] = request.session.get('zmo-user', dict())
    result['scripts_url'] = request.registry.settings.scripts_url
    result['community_host'] = request.registry.settings.community_host + '/'
    result['community_paths'] = {'login': 'user/login',
                                 'register': 'user/register',
                                 'logout': 'logout',
                                 'leserartikel': 'leserartikel',
                                 'newsletter': 'newsletter'}
    return dict(result)


app_info = cornice.service.Service(
    name='appinfo',
    path='/-/',
    renderer='json',
    accept='application/json'
)


@app_info.get()
def get_app_info(request):
    return request.app_info
