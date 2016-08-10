{% extends "zeit.web.core:templates/inc/asset/image.tpl" %}

{% set image = get_image(teaser, variant_id='original', fallback=False) %}
{% set media_caption_additional_class = 'figcaption--hidden' %}
