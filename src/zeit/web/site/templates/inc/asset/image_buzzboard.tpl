{%- extends "zeit.web.core:templates/inc/asset/image_linked.tpl" -%}

{% set image = get_image(teaser, variant_id='wide', fallback=True) %}

{% block media_link_title %}{{ teaser.teaserSupertitle or teaser.supertitle }} - {{ teaser.teaserTitle or teaser.title }}{% endblock %}

{% if image.path in view.buzzboard_images(image.path) %}
    {% set media_container_additional_class = 'teaser-buzzboard__media-container--duplicate' %}
{% endif %}
