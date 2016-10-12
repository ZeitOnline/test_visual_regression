{% extends "zeit.web.core:templates/inc/asset/image.tpl" %}

{% set module_layout = packshot_layout if packshot_layout else 'zplus' %}
{% set image = get_image(packshot) %}
{% block media_caption %}{% endblock %}
