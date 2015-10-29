{%- extends "zeit.web.site:templates/inc/asset/image.tpl" -%}

{% if href %}
{% block media_block_wrapper %}
<a class="{% block media_block_link %}{% endblock %}" title="{{ image.title | hide_none }}" href="{{ href }}"{% if tracking_slug %} data-id="{{ tracking_slug }}image"{% endif %}>
    {{ super() }}
</a>
{% endblock %}
{% endif %}
