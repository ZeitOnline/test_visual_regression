{%- extends "zeit.web.core:templates/inc/asset/image_teaser.tpl" -%}

{% block media_block %}{{ super() }} is-pixelperfect{% endblock %}
{% set omit_image_links = True %}
