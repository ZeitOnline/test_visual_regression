{%- extends "zeit.web.core:templates/inc/asset/image_linked.tpl" -%}

{% set image = get_image(module, fallback=fallback_image) %}
{% set href = teaser | create_url | append_campaign_params %}
{% set media_caption_additional_class = 'figcaption--hidden' %}

{% block media_link_title %}{{ teaser.teaserSupertitle or teaser.supertitle }} - {{ teaser.teaserTitle or teaser.title }}{% endblock %}

{% block media_block_alt %}
     alt="{% if teaser.teaserSupertitle or teaser.supertitle %}{{ (teaser.teaserSupertitle or teaser.supertitle)|e }}: {% endif %}{{ (teaser.teaserTitle or teaser.title)|e }}"
{% endblock %}

{% if module.force_mobile_image %}
    {%- set media_block_additional_class = '{}__media--force-mobile'.format(module_layout) %}
{% endif %}
