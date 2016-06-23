{%- extends "zeit.web.core:templates/inc/asset/image_linked.tpl" -%}

{% set buzzboard_image = get_image(module, teaser, variant_id='wide') %}
{% if buzzboard_image.path not in view.buzzboard_images(buzzboard_image.path) %}
    {% set image = buzzboard_image %}
    {% set media_caption_additional_class = 'figcaption--hidden' %}
    {% set href = image %}
{% endif %}
