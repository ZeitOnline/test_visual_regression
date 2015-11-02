{%- extends "zeit.web.site:templates/inc/image.tpl" -%}

{% block mediablock_additional_data_attributes %}
    {% set mobile_image = get_image(module, teaser, variant_id='wide') %}
    {% if mobile_image %}
    data-mobile-src="{{ request.image_host + mobile_image.path }}" data-mobile-ratio="{{ mobile_image.ratio }}" data-mobile-variant="{{ mobile_image.image_pattern }}"
    {% endif %}
{% endblock %}
