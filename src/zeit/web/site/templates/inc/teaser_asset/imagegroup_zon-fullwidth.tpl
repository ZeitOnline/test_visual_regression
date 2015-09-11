{%- extends "zeit.web.site:templates/inc/teaser_asset/imagegroup.tpl" -%}

{% block mediablock_additional_data_attributes %}
    {% set mobile_image = get_image(module, teaser, variant_id='wide') %}
    {% if mobile_image %}
    data-mobile-src="{{ view.request.route_url('home') + mobile_image.path }}" data-mobile-ratio="{{ mobile_image.ratio | hide_none }}" data-mobile-variant="{{ mobile_image.image_pattern | hide_none }}"
    {% endif %}
{% endblock %}
