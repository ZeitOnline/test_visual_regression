{%- extends "zeit.web.core:templates/inc/asset/image.tpl" -%}

{% set module_layout = 'video-thumbnail' %}
{% block media_block %}{{ module_layout }} {{ module_layout }}--small{% endblock %}
