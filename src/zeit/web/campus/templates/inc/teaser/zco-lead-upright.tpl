{%- extends "zeit.web.campus:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-lead-upright{% endblock %}
{% block teaser_media %}
    {% set module_layout = self.layout() %}
    {% include "zeit.web.campus:templates/inc/teaser/asset/image_zco-lead-upright.tpl" ignore missing %}
{% endblock %}

{% block teaser_content %}
    <div class="{{ self.layout() }}__content">
        {{ super() }}
    </div>
{% endblock %}
