{% extends "zeit.web.core:templates/inc/asset/image.tpl" %}

{% set image = get_image(packshot, fallback='default_packshot_diezeit') %}
{% block media_caption %}{% endblock %}
