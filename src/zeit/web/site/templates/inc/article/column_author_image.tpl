{%- extends "zeit.web.core:templates/inc/asset/image_linked.tpl" -%}

{% if view.authors %}
    {% set href = view.authors[0].href | create_url %}
{% endif %}

{% set module_layout = 'column-heading' %}
