{% extends "zeit.web.core:templates/inc/asset/image.tpl" %}

{% set image = get_image(block.author, fallback=False, variant_id='square') %}
{% set image_itemprop = 'image' %}
{% set module_layout = 'authorbox' %}
{% set media_caption_additional_class = 'figcaption--hidden' %}
{% block media_caption_class %}{{ module_layout }}{% endblock %}
