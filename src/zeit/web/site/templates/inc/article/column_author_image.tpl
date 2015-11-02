{%- extends "zeit.web.site:templates/inc/asset/image_linked.tpl" -%}

{% set image = view.author_img %}
{% if view.authors %}
{% set href = view.authors[0].href | create_url %}
{% endif %}

{% set module_layout = 'column-heading' %}
