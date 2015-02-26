{%- extends "zeit.web.site:templates/inc/linked-image_refactoring.tpl" -%}

{% set image = get_column_image(teaser) %}
{% set href = teaser.uniqueId | translate_url %}

{% block mediablock %}{{ teaser_block_layout }}__media{% endblock %}
{% block mediablock_helper %}{{ teaser_block_layout }}__media-container{% endblock %}
{% block mediablock_link %}{{ teaser_block_layout }}__media-link{% endblock %}
{% block mediablock_item %}{{ teaser_block_layout }}__media-item{% endblock %}
