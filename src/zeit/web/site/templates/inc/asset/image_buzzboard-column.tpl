{% extends "zeit.web.core:templates/inc/asset/image_linked.tpl" %}

{% set image = get_image(teaser, name='author', fallback=True) %}

{% block media_link_title %}{{ teaser.teaserSupertitle or teaser.supertitle }} - {{ teaser.teaserTitle or teaser.title }}{% endblock %}

{% set media_block_additional_class = 'teaser-buzzboard__media--column' %}
{% set media_container_additional_class = 'teaser-buzzboard__media-container--column' %}

{% if image.path in view.buzzboard_images(image.path) %}
    {% set media_container_additional_class = 'teaser-buzzboard__media-container--column teaser-buzzboard__media-container--duplicate' %}
{% endif %}


