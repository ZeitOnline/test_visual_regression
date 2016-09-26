{%- extends "zeit.web.core:templates/inc/asset/image_linked.tpl" -%}

{% set image = get_image(block, fallback=False) %}
{% set module_layout = 'infographic' %}
{% set href = image.href %}
{% set image_itemprop = 'image' %}

{% block media_block %}{{ '%s__media' | format(module_layout) | with_mods(block.display_mode) }}{% endblock %}
{% block media_caption_class %}infographic{% endblock %}

{% block media_caption_above %}
    <h3 class="infographic__headline" itemprop="name">{{ image.title }}</h3>
    {% if image.caption -%}
    <p class="infographic__text" itemprop="caption">{{ image.caption }}</p>
    {%- endif %}
{% endblock %}

{% block media_caption %}
    {%- if image.origin or image.copyrights -%}
        {{ super() }}
    {%- endif -%}
{% endblock %}

{% block media_caption_content %}
    {%- if image.origin -%}
        Quelle: {{ image.origin }}
    {%- endif -%}
    {{ super() }}
{% endblock %}
