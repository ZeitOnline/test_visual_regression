{% extends "zeit.web.core:templates/inc/asset/image.tpl" %}

{% set image = get_image(view.volume.covers['coverimage'], variant_id='cinema', fallback=False) %}
{% set media_block_additional_class = 'is-pixelperfect' -%}
{% set media_caption_additional_class = 'figcaption--hidden' %}

{% block media_block_additional_data_attributes %}
    {%- require mobile_image = get_image(view.volume.covers['coverimage'], variant_id='portrait', fallback=True) %}
        data-mobile-src="{{ request.image_host + mobile_image.path }}" data-mobile-ratio="{{ mobile_image.ratio }}"
    {%- endrequire %}
{% endblock %}
