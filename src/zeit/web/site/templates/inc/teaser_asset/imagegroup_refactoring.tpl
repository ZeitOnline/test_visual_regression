{%- extends "zeit.web.site:templates/inc/linked-image_refactoring.tpl" -%}

{% set image = get_teaser_image(module, teaser) %}
{% set href = teaser.uniqueId | translate_url %}
