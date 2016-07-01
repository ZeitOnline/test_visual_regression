{%- extends "zeit.web.core:templates/inc/asset/image_linked.tpl" -%}

{% set image = get_image(module, teaser, fallback=fallback_image, fallback_expired=fallback_expired) %}
{% set href = teaser | create_url | append_campaign_params %}
{% set media_caption_additional_class = 'figcaption--hidden' %}
{% if module.force_mobile_image %}
    {%- set media_block_additional_class = '{}__media--force-mobile'.format(module_layout) %}
{% endif %}

