{%- extends "zeit.web.core:templates/inc/asset/image_teaser.tpl" -%}

{% block media_block_link %}teaser-square__media-link{% endblock %}

{% block media_block %}{{ super() }} is-pixelperfect{% endblock %}
