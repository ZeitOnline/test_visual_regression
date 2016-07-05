{%- extends "zeit.web.core:templates/inc/asset/image.tpl" -%}

{% block media_block_wrapper %}
{% if href %}
    <a class="{% block media_block_link %}{% endblock %}" title="{{ image.title }}" href="{{ href }}"{% if tracking_slug %} data-id="{{ tracking_slug }}image"{% endif %}>
        {{ super() }}
    </a>
{% else %}
    {{ super() }}
{% endif %}
{% endblock %}

{% block media_block_additional_data_attributes %}
    {% set mobile_image = get_image(module, teaser, variant_id='portrait') %}
    {% if mobile_image %}
    data-mobile-src="{{ request.image_host + mobile_image.path }}" data-mobile-ratio="{{ mobile_image.ratio }}"
    {% endif %}
{% endblock %}
