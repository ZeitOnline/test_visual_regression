{%- extends "zeit.web.core:templates/inc/asset/image_linked.tpl" -%}

{% if view.authors %}
    {% set href = view.authors[0].href | create_url %}
{% endif %}

{% set module_layout = 'column-heading' %}
{% block image_link_additional_data_attributes %}
    data-ct-row="author" data-ct-column="{{ '%s_of_%s' | format(1, view.authors | length) }}" data-ct-subcolumn="false" data-ct-label="image"
{%- endblock %}
