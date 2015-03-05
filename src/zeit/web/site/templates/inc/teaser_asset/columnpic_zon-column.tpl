{%- extends "zeit.web.site:templates/inc/linked-image_refactoring.tpl" -%}

{% set image = get_column_image(teaser) %}
{% set href = teaser.uniqueId | translate_url %}
