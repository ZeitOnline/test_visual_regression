{%- extends "zeit.web.site:templates/inc/asset/image.tpl" -%}

{% set image = get_image(module, teaser, variant_id='original') %}
{% set media_caption_additional_class = 'figcaption--hidden' %}
