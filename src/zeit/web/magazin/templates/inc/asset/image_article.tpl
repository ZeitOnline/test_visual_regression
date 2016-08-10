{% extends "zeit.web.core:templates/inc/asset/image_linked.tpl" %}

{% set image = obj %}
{% set href = image.href %}
{% set image_itemprop = 'image' %}
{% if image.meta %}
    {% set footer_has_border = True if (image.meta.origin and image.copyright) else False %}
{% endif %}

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

{% block media_caption -%}
    <figcaption class="{% block media_caption_class %}figure{% endblock %}__caption {{ media_caption_additional_class }}">
        {% if image.meta and image.meta.origin  %}
        <span class="x-caption--sans">Quelle: {{ image.meta.origin }}</span>
        {% elif image.caption %}
        <span class="figure__text">{{ image.caption | safe }}</span>
        {% endif %}
        {% if image.copyright | count and image.copyright[0][0] != '©' %}
        <span class="{{ self.media_caption_class() }}__copyright" itemprop="copyrightHolder">
            {% if image.copyright[0][1] %}
            <a href="{{ image.copyright[0][1] }}" class="{{ media_copyright_class }}" target="_blank">
            {%- endif -%}
                {{ image.copyright[0][0] }}
            {%- if image.copyright[0][1] -%}
            </a>
            {% endif %}
        </span>
        {% endif %}
    </figcaption>
{%- endblock %}
