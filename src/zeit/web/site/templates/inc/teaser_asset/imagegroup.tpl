{%- extends "zeit.web.site:templates/inc/linked-image.tpl" -%}

{% set image = module | get_image(teaser) %}
{% set href = teaser.uniqueId | create_url %}
