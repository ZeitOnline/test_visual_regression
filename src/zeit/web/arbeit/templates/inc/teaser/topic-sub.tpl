{%- extends "zeit.web.arbeit:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-topic-sub{% endblock %}

{% block teaser_media %}
    {% set module_layout = self.layout() %}
    {% include "zeit.web.arbeit:templates/inc/teaser/asset/image_teaser.tpl" %}
{% endblock %}

{% block teaser_container %}{% endblock %}
