{%- extends "zeit.web.site:templates/inc/linked-image.tpl" -%}

{% set image = get_image(module, teaser) %}
{% set href = teaser | create_url %}
