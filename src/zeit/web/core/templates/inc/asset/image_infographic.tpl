{%- extends "zeit.web.core:templates/inc/asset/image_linked.tpl" -%}

{% set image = get_image(block, fallback=False) %}
{% set module_layout = 'infographic' %}
{% set href = image.href %}
{% set image_itemprop = 'image' %}
{% set media_block_additional_class = 'high-resolution' %}
{% set display_mode = 'large' if block == view.header_module else block.display_mode %}

{% block media_block %}{{ '%s__media' | format(module_layout) | with_mods(display_mode) }}{% endblock %}
{% block media_caption_class %}infographic{% endblock %}
{% block image_additional_data_attributes %} data-ct-block="infographic"{% endblock %}
{% block image_link_additional_data_attributes %} data-ct-label="image"{% endblock %}

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
