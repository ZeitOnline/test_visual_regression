{% extends "zeit.web.core:templates/inc/asset/image_linked.tpl" %}

{% set image = get_image(view.header_module, fallback=False) %}
{% set href = image.href %}
{% set image_itemprop = 'image' %}
{% set module_layout = 'header-article' %}
{% block media_caption_class %}{{ module_layout }}{% endblock %}
{% block image_link_additional_data_attributes %} data-ct-row="image" data-ct-column="false" data-ct-label="image"{% endblock %}
