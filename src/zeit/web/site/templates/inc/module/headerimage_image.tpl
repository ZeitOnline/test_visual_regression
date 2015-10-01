{%- extends "zeit.web.site:templates/inc/image.tpl" -%}

{% block mediablock_additional_data_attributes %}
    {% set mobile_image = get_image(module, teaser, variant_id='cinema') %}
    {% if mobile_image %}
    data-mobile-src="{{ request.image_host + mobile_image.path }}" data-mobile-ratio="{{ mobile_image.ratio | hide_none }}" data-mobile-variant="{{ mobile_image.image_pattern | hide_none }}"
    {% endif %}
{% endblock %}
