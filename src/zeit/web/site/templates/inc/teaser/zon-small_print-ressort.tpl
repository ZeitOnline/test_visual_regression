{%- extends "zeit.web.site:templates/inc/teaser/zon-small.tpl" -%}

{% block zplus_data %}{% endblock %}

{% block content_kicker_logo %}
    {% set logo_layout = self.layout() %}
    {% for template in teaser | logo_icon(area.kind, zplus='skip') %}
        {% include "zeit.web.core:templates/inc/badges/{}.tpl".format(template) %}
    {% endfor %}
{% endblock %}

{% block teaser_datetime %}{% endblock %}
