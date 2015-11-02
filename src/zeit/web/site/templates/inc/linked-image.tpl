{%- extends "zeit.web.site:templates/inc/image.tpl" -%}

{% block mediablock_wrapper %}
{% if href %}
	<a class="{% block mediablock_link %}{% endblock %}" title="{{ image.attr_title | hide_none }}" href="{{ href }}"{% if tracking_slug %} data-id="{{ tracking_slug }}image"{% endif %}>
		{{ super() }}
	</a>
{% else %}
	{{ super() }}
{% endif %}
{% endblock %}
