{%- extends "zeit.web.site:templates/inc/teaser/default_refactoring.tpl" -%}

{% block teaser_media_position_after_title %}
    {% with -%}
        {% set class = 'buzz-line' %}
        {% set icon = module.layout %}
        {% set label = teaser.score %}
        {% set modifier = module.layout %}
        {% include "zeit.web.site:templates/inc/teaser_asset/annotation.tpl" with context %}
    {%- endwith %}
{% endblock %}

{% block teaser_container %}{% endblock %}
