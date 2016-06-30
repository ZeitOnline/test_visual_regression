{%- extends "zeit.web.core:templates/inc/asset/image.tpl" -%}

{% set image = get_image(module, teaser, fallback=True, fallback_expired=True) %}
{% block media_caption %}{% endblock %}
