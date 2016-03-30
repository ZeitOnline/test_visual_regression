{%- extends "zeit.web.core:templates/inc/asset/image.tpl" -%}

{% set image = get_image(module, teaser, fallback=False) %}
{% block media_caption %}{% endblock %}
