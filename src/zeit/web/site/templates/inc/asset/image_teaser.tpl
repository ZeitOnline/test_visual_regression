{%- extends "zeit.web.site:templates/inc/asset/image_linked.tpl" -%}

{% set image = get_image(module, teaser, fallback=False) %}
{% set href = teaser | create_url | append_campaign_params %}
{% set media_caption_additional_class = 'figcaption--hidden' %}
