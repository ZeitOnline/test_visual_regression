{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block teaser_journalistic_format %}{% endblock %}

{% block teaser_media_position_after_title %}
    {% with -%}
        {% set class = 'buzz-line' %}
        {% set icon = module.layout.id %}
        {% set label = teaser.score %}
        {% set modifier = module.layout %}
        {% include "zeit.web.site:templates/inc/teaser_asset/annotation.tpl" %}
    {%- endwith %}
{% endblock %}

{% block teaser_container %}{% endblock %}
