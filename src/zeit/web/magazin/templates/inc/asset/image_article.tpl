{% extends "zeit.web.core:templates/inc/asset/image_linked.tpl" %}

{% set image = get_image(obj, fallback=False) %}
{% set href = image.href %}
{% set image_itemprop = 'image' %}

{% block media_block -%}
{{ {'large': 'figure-full-width',
    'column-width': 'figure is-constrained is-centered',
    'medium-float-left': 'figure-horizontal',
    'medium-float-right': 'figure-horizontal--right',
    'small-float-right': 'figure-stamp--right'}.get(
        obj.display_mode, 'figure-stamp') }}
{%- endblock %}

{% block media_block_helper -%}
figure__media-container
{%- endblock %}

{% block media_block_item -%}
figure__media
{%- endblock %}

{% block media_caption_content -%}
    {% if image.caption -%}
        <span class="figure__text">{{ image.caption }}</span>
    {% endif %}
    {{ super() }}
{%- endblock %}
