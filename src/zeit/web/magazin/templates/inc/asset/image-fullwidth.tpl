{%- extends "zeit.web.magazin:templates/inc/asset/image_teaser.tpl" -%}

{% block media_block_additional_data_attributes %}
    {% set mobile_image = get_image(module, variant_id='portrait') %}
    {% if mobile_image %}
    data-mobile-src="{{ request.image_host + mobile_image.path }}" data-mobile-ratio="{{ mobile_image.ratio }}"
    {% endif %}
{% endblock %}
