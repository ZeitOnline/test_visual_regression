{%- extends "zeit.web.core:templates/inc/asset/image.tpl" -%}

{% set image = get_image(obj, fallback=False) %}

{% block media_block %}photocluster__figure{% endblock %}
{% set module_layout = 'photocluster' %}
{% set media_caption_additional_class = 'figcaption--hidden' %}
