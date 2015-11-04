{%- extends "zeit.web.site:templates/inc/asset/image_linked.tpl" -%}

{% set image = get_image(module, teaser, variant_id='original') %}
{% set media_caption_additional_class = 'figcaption--hidden' %}
{% set href = teaser | create_url %}
