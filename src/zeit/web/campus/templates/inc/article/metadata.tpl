{% extends "zeit.web.site:templates/inc/article/metadata.tpl" %}

{%- block metadata_time %}
    {{ view.date_first_released | format_date('short') }}, Aktualisiert am {{ view.date_last_modified | format_date('short') }}
{%- endblock %}
