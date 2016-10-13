{% set image = get_image(view.volume.covers['coverimage'], variant_id='original', fallback=False) %}

{% extends "zeit.web.core:templates/inc/asset/image.tpl" %}
{% block module_layout%}volume-header{% endblock %}

{% block media_block_additional_data_attributes %}
    {%- require mobile_image = get_image(view.volume.covers['coverimage'], variant_id='portrait', fallback=True) %}
        data-mobile-src="{{ request.image_host + mobile_image.path }}" data-mobile-ratio="{{ mobile_image.ratio }}"
    {%- endrequire %}
{% endblock %}
