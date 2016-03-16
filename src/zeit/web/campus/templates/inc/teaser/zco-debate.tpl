{# this is the teaser variant of the debate module #}

{%- extends "zeit.web.campus:templates/inc/shared/debate.tpl" -%}

{% set block = module %}

{% block wrapper_start %}
    <article class="teaser-debate" data-unique-id="{{ teaser.uniqueId }}" data-meetrics="{{ area.kind }}" data-clicktracking="{{ area.kind }}">
{% endblock %}

{% block wrapper_end %}
    </article>
{% endblock %}
