{%- extends "zeit.web.site:templates/inc/asset/image.tpl" -%}

{% set module_layout = 'gallery' %}

{% set media_block_additional_class = 'slide' %}

{% block media_caption_content %}
    <span class="figure__index">{{ index | hide_none }}</span>
    <span class="figure__text">{{ image.caption | hide_none }}</span>
    {{ super() }}
{% endblock %}
