{# TODO: rawr toggelbar machen? Hat das einen Wert? #}
<script type="text/javascript">
{# A RawrConfig object must be accessible in the global JavaScript namespace.
 # It must contain the key 'location_metadata', which must be JSON
 # conform and serializable.
 # Date and time formats must be ISO 8601 formatted.
 #}

window.RawrConfig = {
    location_metadata: {
        'article_id': '{{ view.content_path }}',
        'published': '{{ view.date_last_published_semantic | format_date('iso8601') }}',
        'description': '{{ view.title }}',
        'channels': [{% if view.context.channels and view.context.channels[0] and view.context.channels[0] | length > 0 %}{% for channel in view.context.channels[0] -%}
            '{{ channel }}'{% if not loop.last %}, {% endif -%}
            {%- endfor %}{% endif %}],
        'ressorts': [{% if view.ressort %}'{{ view.ressort }}'{% if view.sub_ressort %}, '{{ view.sub_ressort }}'{% endif %}{% endif %}],
        'tags': [{%- for tag in view.ranked_tags -%}
            '{{ tag.label }}'{%- if not loop.last %}, {% endif -%}
            {%- endfor -%}],
        'meta': {
            'description': '{{ view.title }}'
        }
    }
};
</script>
