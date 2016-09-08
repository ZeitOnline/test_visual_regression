{% extends "zeit.web.core:templates/inc/asset/image_linked.tpl" %}

{% set module_layout = 'zplus' %}
{% set image = get_image(view.zplus_label.cover) %}
{% block media_caption %}{% endblock %}
