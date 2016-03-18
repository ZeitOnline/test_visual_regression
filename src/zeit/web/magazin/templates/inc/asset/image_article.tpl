{% extends "zeit.web.core:templates/inc/asset/image_linked.tpl" %}

{% set image = get_image(content=obj, variant_id=obj.layout.variant if obj.layout else None, fallback=False) or obj %}
{% set href = image.href %}

{% block media_block -%}
{{ {'large': 'figure-full-width',
    'zmo-large-center': 'figure-full-width',
    'zmo-medium-left': 'figure-horizontal',
    'zmo-medium-right': 'figure-horizontal--right',
    'zmo-medium-center': 'figure is-constrained is-centered',
    'zmo-small-left': 'figure-stamp',
    'zmo-small-left-original': 'figure-stamp',
    'zmo-small-right': 'figure-stamp--right',
    'zmo-small-right-original': 'figure-stamp--right'}.get(
        obj.layout.id, 'figure-stamp') }}
{%- endblock %}

{% block media_block_helper -%}
figure__media-container
{%- endblock %}

{% block media_block_item -%}
figure__media
{%- endblock %}

{% block media_caption -%}
    <figcaption class="figure__caption">
        {% if image.caption %}
        <span class="figure__text">{{ image.caption | safe }}</span>
        {% endif %}
        {% if image.copyright | count and image.copyright[0][0] != '©' %}
        <span class="figure__copyright" itemprop="copyrightHolder">
            {% if image.copyright[0][1] %}
            <a href="{{ image.copyright[0][1] }}" target="_blank">
            {% endif %}
                {{ image.copyright[0][0] }}
            {% if image.copyright[0][1] %}
            </a>
            {% endif %}
        </span>
        {% endif %}
    </figcaption>
{%- endblock %}
