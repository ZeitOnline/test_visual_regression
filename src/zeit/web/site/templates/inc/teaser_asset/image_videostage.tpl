{%- extends "zeit.web.site:templates/inc/image.tpl" -%}

{% set module_layout = 'video-thumbnail' %}
{% block mediablock %}{{ module_layout }} {{ module_layout }}--large{% endblock %}
