{%- extends "zeit.web.site:templates/inc/linked-image_refactoring.tpl" -%}

{% set image = get_teaser_image(teaser_block, teaser) %}
{% set href = teaser.uniqueId | translate_url %}
