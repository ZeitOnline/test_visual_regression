{%- extends "zeit.web.core:templates/inc/asset/image_linked.tpl" -%}

{% set image = get_gallery_image(module, teaser) %}
{% set href = module.read_more_url %}
{% block media_caption_class %}{{ module_layout }}{% endblock %}

{% block media_caption_content %}
    <span class="{{ module_layout }}__text" itemprop="caption">{{ image.caption | trim }}</span>
    {{ super() }}
{% endblock %}
{% block media_link_title %}Fotografie - Gesammelte Momente{% endblock %}
