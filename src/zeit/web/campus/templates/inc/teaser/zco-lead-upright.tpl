{%- extends "zeit.web.campus:templates/inc/teaser/default.tpl" -%}

{# TODO: Verstehen: Warum kommt dieser Block zwei Zeilen später als self.layout() an ? #}
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
