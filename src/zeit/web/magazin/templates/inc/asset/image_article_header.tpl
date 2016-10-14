{% extends "zeit.web.core:templates/inc/asset/image_linked.tpl" %}

{% set image = get_image(view.header_module, fallback=False) %}
{% set href = image.href %}
{% set image_itemprop = 'image' %}
{% set module_layout = 'article__head' %}
{% block media_caption_class %}{{ module_layout }}{% endblock %}
