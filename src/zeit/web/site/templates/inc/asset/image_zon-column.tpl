{% extends "zeit.web.core:templates/inc/asset/image_linked.tpl" %}

{% set image = get_column_image(teaser) %}
{% set href = teaser.uniqueId | create_url %}

{% block media_link_title %}{{ teaser.teaserSupertitle or teaser.supertitle }} - {{ teaser.teaserTitle or teaser.title }}{% endblock %}
