{% extends "zeit.web.core:templates/inc/asset/image_linked.tpl" %}

{% set buzzboard_image = get_image(teaser, name='author', fallback=False) %}
{% if buzzboard_image.path not in view.buzzboard_images(buzzboard_image.path) %}
    {% set image = buzzboard_image %}
    {% set href = teaser.uniqueId | create_url %}
{% endif %}
