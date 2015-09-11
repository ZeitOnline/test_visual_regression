{%- extends "zeit.web.site:templates/inc/linked-image.tpl" -%}

{% set image = get_image(module, teaser, variant_id='wide') %}
{% set href = teaser.uniqueId | create_url %}
