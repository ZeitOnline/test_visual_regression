import cornice.service
import pyramid.security
import pyramid.settings


def assemble_app_info(request):
    settings = request.registry.settings
    return dict(
        authenticated=bool(pyramid.security.authenticated_userid(request)),
        community_host=request.registry.settings.community_host + '/',
        community_paths={'login': 'user/login',
                         'register': 'user/register',
                         'logout': 'logout',
                         'leserartikel': 'leserartikel',
                         'newsletter': 'newsletter'},
        debug=pyramid.settings.asbool(settings.get('debug', False)),
        scripts_url=request.registry.settings.scripts_url,
        user=request.session.get('zmo-user', {})
    )


app_info = cornice.service.Service(
    name='appinfo',
    path='/-/',
    renderer='json',
    accept='application/json'
)


@app_info.get()
def get_app_info(request):
    return request.app_info
