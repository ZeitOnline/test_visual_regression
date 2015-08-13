{%- extends "zeit.web.site:templates/inc/image.tpl" -%}

{% block mediablock_additional_data_attributes %}
    {% set mobile_image = image.image_group | get_variant('cinema') %}
    data-mobile-src="{{ view.request.route_url('home') + mobile_image.path }}" data-mobile-ratio="{{ mobile_image.ratio | hide_none }}" data-mobile-variant="{{ mobile_image.image_pattern | hide_none }}"
{% endblock %}
