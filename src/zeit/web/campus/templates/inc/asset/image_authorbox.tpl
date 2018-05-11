{% extends "zeit.web.core:templates/inc/asset/image.tpl" %}

{% set image = get_image(block.author, fallback=False, fill_color='535560', variant_id='wide') %}
{% set image_itemprop = 'image' %}
{% set module_layout = 'authorbox' %}
{% set media_caption_additional_class = 'figcaption--hidden' %}
{% block media_caption_class %}{{ module_layout }}{% endblock %}

{% block media_block_additional_data_attributes %}
    {% set mobile_image = get_image(block.author, variant_id='square', fallback=False, fill_color='535560') %}
    {% if mobile_image %}
        data-mobile-src="{{ request.image_host + mobile_image.path }}" data-mobile-ratio="{{ mobile_image.ratio }}"
    {% endif %}
{% endblock %}
