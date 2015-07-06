{%- extends "zeit.web.site:templates/inc/linked-image.tpl" -%}

{% set image = get_teaser_image(module, teaser) %}
{% set href = teaser.uniqueId | create_url %}
