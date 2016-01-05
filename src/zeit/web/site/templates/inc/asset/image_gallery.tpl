{%- extends "zeit.web.site:templates/inc/asset/image.tpl" -%}

{% set module_layout = 'gallery' %}

{% set media_block_additional_class = 'slide' %}

{% block media_block_item %}figure__media{% endblock %}

{% block media_caption_content %}
    {# NOTE: remove the '+ 1' when Jinja version was upgraded to >= 2.8, older versions count wrong #}
    <span class="figure__index">{{ image_loop.index }}/{{ image_loop.length + 1 }}</span>
    <span class="figure__text">{{ image.caption }}</span>
    {{ super() }}
{% endblock %}
