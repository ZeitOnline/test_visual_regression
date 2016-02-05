{%- extends "zeit.web.core:templates/inc/asset/image.tpl" -%}

{% set module_layout = 'card' %}
{% set image = get_image(module, teaser, variant_id='large') %}
{% set media_caption_additional_class = 'figcaption--hidden' %}
