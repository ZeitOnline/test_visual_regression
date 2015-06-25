{%- extends "zeit.web.site:templates/inc/linked-image.tpl" -%}

{% set image = view.author_img %}
{% set href = view.authors[0].href | create_url %}

{% set module_layout = 'column-heading' %}
