{%- extends "zeit.web.campus:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-square{% endblock %}
{% block teaser_media %}
    {% set module_layout = self.layout() %}
    {% include "zeit.web.campus:templates/inc/teaser/asset/image_teaser.tpl" %}
{% endblock %}
