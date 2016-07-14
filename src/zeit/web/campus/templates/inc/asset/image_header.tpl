{%- extends "zeit.web.core:templates/inc/asset/image.tpl" -%}

{% set module_layout = "header-image" %}
{% set media_caption_additional_class = 'figcaption--hidden' %}

{% block media_block_helper %}{{ super() | with_mods('animated' if module.animate) }}{% endblock %}
