{%- extends "zeit.web.core:templates/inc/asset/image_teaser.tpl" -%}

{% block media_block_link %}teaser-fullwidth__media-link{% endblock %}

{% block media_block_additional_data_attributes %}
    {% set mobile_image = get_image(module, variant_id='wide') %}
    {% if mobile_image %}
    data-mobile-src="{{ request.image_host + mobile_image.path }}" data-mobile-ratio="{{ mobile_image.ratio }}"
    {% endif %}
{% endblock %}
