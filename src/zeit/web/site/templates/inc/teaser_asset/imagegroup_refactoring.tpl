{%- extends "zeit.web.site:templates/inc/image_refactoring.tpl" -%}

{% block mediablock_helper %}{{ teaser_block_layout }}__media{% endblock %}
{% block mediablock %}{{ teaser_block_layout }}__media-container{% endblock %}
{% block mediablock_link %}{{ teaser_block_layout }}__media-link{% endblock %}
{% block mediablock_item %}{{ teaser_block_layout }}__media-item{% endblock %}
