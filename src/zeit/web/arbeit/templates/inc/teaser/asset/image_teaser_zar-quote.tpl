{% extends "zeit.web.core:templates/inc/asset/image_linked.tpl" %}

{% set image = get_image(teaser, variant_id = 'square', name='author', fallback=False) %}
{% set href = teaser.uniqueId | create_url %}
{% set media_caption_additional_class = 'figcaption--hidden' %}

{% block media_link_title %}{{ teaser.teaserSupertitle or teaser.supertitle }} - {{ teaser.teaserTitle or teaser.title }}{% endblock %}
