{%- extends "zeit.web.campus:templates/inc/teaser/asset/image_teaser.tpl" -%}

{% block media_block_additional_data_attributes %}
    {% set mobile_image = get_image(module, variant_id='wide', fallback=True) %}
    {% if mobile_image %}
    data-mobile-src="{{ request.image_host + mobile_image.path }}" data-mobile-ratio="{{ mobile_image.ratio }}"
    {% endif %}
{% endblock %}
