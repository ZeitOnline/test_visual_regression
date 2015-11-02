{%- extends "zeit.web.site:templates/inc/asset/image_linked.tpl" -%}

{% set image = get_image(module, teaser, variant_id='original') %}
{% set href = teaser | create_url %}
