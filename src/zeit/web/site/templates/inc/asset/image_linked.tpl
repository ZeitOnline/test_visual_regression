{%- extends "zeit.web.site:templates/inc/asset/image.tpl" -%}

{% block media_block_wrapper %}
{% if href %}
	<a class="{% block media_block_link %}{% endblock %}" title="{{ image.title }}" href="{{ href }}"{% if tracking_slug %} data-id="{{ tracking_slug }}image"{% endif %}>
		{{ super() }}
	</a>
{% else %}
	{{ super() }}
{% endif %}
{% endblock %}
