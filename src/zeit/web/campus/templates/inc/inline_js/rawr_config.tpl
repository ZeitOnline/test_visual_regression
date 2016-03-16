{# TODO: rawr toggelbar machen? Hat das einen Wert? #}
<script>
{# A RawrConfig object must be accessible in the global JavaScript namespace.
 # It must contain the key 'location_metadata', which must be JSON
 # conform and serializable.
 # Date and time formats must be ISO 8601 formatted.
 #}

{# OPTIMIZE: jsonify(tags, ressorts, channels) #}

window.RawrConfig = {
    location_metadata: {
        'article_id': '{{ view.content_path }}',
        'published': '{{ view.date_last_published_semantic | format_date('iso8601') }}',
        'description': '{{ view.title }}',
        'channels': [],
        'ressorts': [{% if view.ressort %}{{ view.ressort }}{% if view.sub_ressort %}, '{{ view.sub_ressort }}'{% endif %}{% endif %}],
        'tags': [{%- for tag in view.ranked_tags -%}
            '{{ tag.label }}'{%- if not loop.last %}, {% endif -%}
            {%- endfor -%}],
        'meta': {
            'description': '{{ view.title }}'
        }
    }
};
</script>
