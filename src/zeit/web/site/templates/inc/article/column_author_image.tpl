{%- extends "zeit.web.site:templates/inc/linked-image.tpl" -%}

{% set image = view.authors[0].image %}
{% set href = view.authors[0].href | translate_url %}

{% set module_layout = 'column-heading' %}
