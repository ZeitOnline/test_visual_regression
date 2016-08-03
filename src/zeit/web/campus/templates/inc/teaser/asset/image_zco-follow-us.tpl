{%- extends "zeit.web.core:templates/inc/asset/image.tpl" -%}

{% set image = get_image(module, fallback=True) %}
{% block media_caption %}{% endblock %}
