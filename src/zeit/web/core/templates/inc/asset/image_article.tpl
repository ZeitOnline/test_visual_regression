{%- extends "zeit.web.core:templates/inc/asset/image_linked.tpl" -%}

{% set module_layout = 'article' %}
{% set href = image.href %}
{% set image_itemprop = 'image' %}

{% set media_block_additional_class = 'article__item' | with_mods(*image.figure_mods) %}

{% set media_caption_additional_class = 'figure__caption--marginalia' if image.layout == 'small' else '' %}

{% block media_caption_content %}
    <span class="figure__text" itemprop="caption">{{ image.caption }}</span>
    {{ super() }}
{% endblock %}
