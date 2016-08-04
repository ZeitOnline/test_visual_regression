{%- extends "zeit.web.core:templates/inc/asset/image.tpl" -%}

{% set media_caption_additional_class = 'figcaption--hidden' %}
{% block media_block_additional_data_attributes %}
    {% set mobile_image = get_image(module, variant_id='wide') %}
    {% if mobile_image %}
    data-mobile-src="{{ request.image_host + mobile_image.path }}" data-mobile-ratio="{{ mobile_image.ratio }}"
    {% endif %}
{% endblock %}
