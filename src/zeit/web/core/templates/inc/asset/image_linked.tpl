{%- extends "zeit.web.core:templates/inc/asset/image.tpl" -%}

{% block media_block_wrapper %}
{% if href and not omit_image_links %}
    <a class="{% block media_block_link %}{% endblock %}" title="{% block media_link_title %}{{ image.title }}{% endblock %}" href="{{ href }}"{% if tracking_slug %} data-id="{{ tracking_slug }}image"{% endif %}>
        {{ super() }}
    </a>
{% else %}
    {{ super() }}
{% endif %}
{% endblock %}
