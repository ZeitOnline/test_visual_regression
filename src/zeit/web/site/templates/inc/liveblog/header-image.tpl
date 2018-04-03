{%- extends "zeit.web.core:templates/inc/asset/image.tpl" -%}

{% set image = get_image(view.header_module, fallback=False) %}
{% set module_layout = 'liveblog-heading' %}
{% set media_caption_additional_class = 'figcaption--hidden' %}
{% set image_itemprop = 'image' %}
