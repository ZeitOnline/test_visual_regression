{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-author{% endblock %}

{% block teaser_kicker %}
    {{ teaser.display_name }}
{% endblock %}
