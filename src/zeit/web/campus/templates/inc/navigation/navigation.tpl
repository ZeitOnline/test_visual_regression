ZEIT CAMPUS

{% require topics = view.context | topic_links %}
    <h3>{{ topics.title }}</h3>
    {% for label, link in topics %}
        <a href="{{ link }}">{{ label }}</a>
    {% endfor %}
{% endrequire %}

{# XXX This is how the login state would be included via ESI
{% set esi_source = '{}login-state?for=campus&context-uri={}'.format(request.route_url('home'), request.url) %}
{{ insert_esi(esi_source, 'Anmeldung nicht möglich') }}
#}
