{% extends "zeit.web.core:templates/inc/asset/image_linked.tpl" %}

{% set image = get_image(block, fallback=False) %}
{% set href = image.href %}
{% set image_itemprop = 'image' %}

{% block media_block -%}
{{ {'large': 'figure-full-width',
    'column-width': 'figure is-constrained is-centered',
    'small-float-right': 'figure-stamp--right'}.get(
        block.display_mode, 'figure-stamp') }}
{%- endblock %}

{% block media_block_helper -%}
figure__media-container
{%- endblock %}

{% block media_block_item -%}
figure__media
{%- endblock %}

{% block media_caption_content -%}
    {% if image.caption -%}
        <span class="figure__text" itemprop="caption">{{ image.caption }}</span>
    {% endif %}
    {{ super() }}
{%- endblock %}
