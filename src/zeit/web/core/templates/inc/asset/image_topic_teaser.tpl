{%- extends "zeit.web.core:templates/inc/asset/image_teaser.tpl" -%}

{% if area.referenced_cp is not none %}
    {% set teaser = area.referenced_cp %}
{% endif %}

{% block media_block %}{{ super() }} is-pixelperfect{% endblock %}

{% block media_block_additional_data_attributes %}
    {%- set mobile_image = get_image(module, teaser, variant_id='square') %}
    {%- if mobile_image %}
    data-mobile-src="{{ request.image_host + mobile_image.path }}" data-mobile-ratio="{{ mobile_image.ratio }}" data-mobile-variant="{{ mobile_image.image_pattern }}"
    {%- endif %}
{% endblock %}
