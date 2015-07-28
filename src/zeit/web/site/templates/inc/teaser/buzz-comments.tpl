{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block teaser_journalistic_format %}{% endblock %}

{% block teaser_media_position_after_title %}
    {% with -%}
        {% set class = 'buzz-line' %}
        {% set label = teaser.score | pluralize('Keine Kommentare', '{} Kommentar', '{} Kommentare') %}
        {% set modifier = module.layout %}
        {% include "zeit.web.site:templates/inc/teaser_asset/annotation.tpl" %}
    {%- endwith %}
{% endblock %}

{% block teaser_container %}{% endblock %}
