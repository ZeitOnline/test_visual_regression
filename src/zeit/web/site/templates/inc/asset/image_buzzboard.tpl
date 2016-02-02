{%- extends "zeit.web.core:templates/inc/asset/image_linked.tpl" -%}

{% set image = get_image(module, teaser, variant_id='wide') %}
{% set media_caption_additional_class = 'figcaption--hidden' %}
{% set href = teaser.uniqueId | create_url %}
