{# TODO: Should rawr be toggle-able? #}
<script type="text/javascript">
{% set string_joiner = '\', \'' | safe %}

window.rawrConfig = {
{% if provides(view.context, 'zeit.cms.content.interfaces.ICommonMetadata') %}
    'locationMetaData': {
        'ident': '{{ view.content_path }}',
        'article_id': '{{ view.content_path }}',
        'published': '{{ view.date_last_modified | format_date('iso8601') }}',
        'description': '{{ view.title | replace("\'", "\\\'") | safe }}',
        'channels': [{% if view.context.channels and view.context.channels[0] and view.context.channels[0] | length > 0 -%}
            '{{ view.context.channels[0] | map('trim') | join(string_joiner) }}'
            {%- endif %}],
        'ressorts': [{% if view.ressort %}'{{ view.ressort }}'{% if view.sub_ressort %}, '{{ view.sub_ressort }}'{% endif %}{% endif %}],
        'tags': [{% if view.keywords -%}
            '{{ view.keywords | join(string_joiner, attribute='label') }}'
            {%- endif %}],
        'meta': {
            'description': '{{ view.title | replace("\'", "\\\'") | safe }}'
        },
        'series': '{{ view.serie | replace("\'", "\\\'") | safe }}'
    },
{% endif %}

    'authProviders': {
        'sso': true,
        'email': false,
        'oauth': false
    }
};
</script>
