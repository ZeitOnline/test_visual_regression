{%- extends "zeit.web.core:templates/inc/asset/image.tpl" -%}

{% set module_layout = 'gallery' %}

{% set media_block_additional_class = 'slide' %}

{% block media_caption_content %}
    <span class="figure__index">{{ image_loop.index }}/{{ image_loop.length }}</span>
    <span class="figure__text">{{ image.caption }}</span>
    {{ super() }}
{% endblock %}
