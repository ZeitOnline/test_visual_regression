{%- extends "zeit.web.core:templates/inc/asset/image.tpl" -%}

{% set module_layout = "header-image" %}
{% set media_caption_additional_class = 'figcaption--hidden' %}

{% block media_block_additional_data_attributes %}
    {% set mobile_image = get_image(module, fallback=False, variant_id='cinema') %}
    {% if mobile_image %}
    data-mobile-src="{{ request.image_host + mobile_image.path }}" data-mobile-ratio="{{ mobile_image.ratio }}" data-mobile-variant="{{ mobile_image.image_pattern }}"
    {% endif %}
{% endblock %}

