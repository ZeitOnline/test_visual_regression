{% extends "zeit.web.core:templates/inc/asset/image.tpl" %}

{% set image = get_image(view.header_module, fallback=False) %}
{% set image_itemprop = 'image' %}
{% set module_layout = 'longform-header' %}
{% set media_caption_additional_class = 'figcaption--hidden' %}
{% set media_block_additional_class = 'is-pixelperfect' -%}

{% block media_caption_class %}{{ module_layout }}{% endblock %}
