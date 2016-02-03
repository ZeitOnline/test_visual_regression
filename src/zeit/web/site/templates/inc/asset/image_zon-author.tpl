{%- extends "zeit.web.core:templates/inc/asset/image.tpl" -%}

{% set image = get_variant(teaser.image_group, 'portrait') %}
{% set module_layout = 'teaser-author' %}

{% block media_caption_content %}{% endblock %}
