{%- extends "zeit.web.campus:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-topic-small{% endblock %}
{% block teaser_container %}{% endblock %}
{% block teaser_media %}
    {% set module_layout = self.layout() %}
    {% include "zeit.web.core:templates/inc/asset/image_teaser.tpl" ignore missing %}
{% endblock %}
