{%- extends "zeit.web.campus:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-wide-large{% endblock %}
{% block teaser_media %}
    {% if not exclude_image %}
        {% set module_layout = self.layout() %}
        {% include "zeit.web.core:templates/inc/asset/image_teaser.tpl" ignore missing %}
    {% endif %}
{% endblock %}
