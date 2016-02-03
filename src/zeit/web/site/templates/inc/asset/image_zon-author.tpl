{%- extends "zeit.web.core:templates/inc/asset/image.tpl" -%}

{% set image = get_variant(teaser.image_group, 'portrait') %}
{% set module_layout = 'author-teaser' %}

{% block media_caption_content %}{% endblock %}
