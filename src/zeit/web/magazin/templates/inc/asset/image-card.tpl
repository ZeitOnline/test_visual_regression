{%- extends "zeit.web.core:templates/inc/asset/image.tpl" -%}

{% set module_layout = 'card' %}
{% set image = get_image(module, variant_id='original', fill_color=None, fallback=True) %}
{% set media_caption_additional_class = 'figcaption--hidden' %}
