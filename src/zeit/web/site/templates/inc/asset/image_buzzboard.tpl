{%- extends "zeit.web.site:templates/inc/asset/image_linked.tpl" -%}

{% set image = get_image(module, teaser, variant_id='wide') %}
{% set href = teaser.uniqueId | create_url %}
