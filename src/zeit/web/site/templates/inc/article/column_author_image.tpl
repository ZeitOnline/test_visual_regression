{%- extends "zeit.web.site:templates/inc/linked-image_refactoring.tpl" -%}

{% set image = view.authors[0].image %}
{% set href = view.authors[0].href | translate_url %}

{% set teaser_block_layout = 'column-heading' %}

{{ super() }}
