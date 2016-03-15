{%- extends "zeit.web.campus:templates/inc/shared/debate.tpl" -%}

{% set block = teaser %}

{% block kicker %}{{ block.supertitle }}{% endblock %}

{% block text %}
    {% for title, text in block.contents %}
        {{ text }}
    {% endfor %}
{% endblock %}

{% block wrapper_start %}
    <article class="teaser-debate" data-unique-id="{{ teaser.uniqueId }}" data-meetrics="{{ area.kind }}" data-clicktracking="{{ area.kind }}">
{% endblock %}

{% block wrapper_end %}
    </article>
{% endblock %}
