{%- extends "zeit.web.core:templates/inc/asset/image_linked.tpl" -%}

{% set buzz_image = get_image(module, teaser, variant_id='wide') %}
{% if buzz_image.path not in view.buzz_images(buzz_image.path) %}
    {% set image = buzz_image %}
    {% set media_caption_additional_class = 'figcaption--hidden' %}
    {% set href = image %}
{% endif %}
