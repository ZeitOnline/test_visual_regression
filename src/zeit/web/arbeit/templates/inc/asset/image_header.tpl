{%- extends "zeit.web.core:templates/inc/asset/image.tpl" -%}

{% set module_layout = "header-image" %}
{% set media_caption_additional_class = 'figcaption--hidden' %}

{#- accomodate multi-line titles & subtitles on mobile advertorial-cps -#}
{% block media_block_additional_data_attributes %}
    {% set mobile_image = get_image(module, fallback=False, variant_id='wide') %}
    {% if mobile_image %}
    data-mobile-src="{{ request.image_host + mobile_image.path }}" data-mobile-ratio="{{ mobile_image.ratio }}"
    {% endif %}
{% endblock %}
