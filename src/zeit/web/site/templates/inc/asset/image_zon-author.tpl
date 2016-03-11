{%- extends "zeit.web.core:templates/inc/asset/image.tpl" -%}

{% set image = get_image(content=teaser, variant_id='portrait', fallback=False) %}

{% block media_caption %}{% endblock %}
