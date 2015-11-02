{%- extends "zeit.web.site:templates/inc/image.tpl" -%}

{% if href %}
{% block mediablock_wrapper %}
<a class="{% block mediablock_link %}{% endblock %}" title="{{ image.attr_title }}" href="{{ href }}"{% if tracking_slug %} data-id="{{ tracking_slug }}image"{% endif %}>
    {{ super() }}
</a>
{% endblock %}
{% endif %}
