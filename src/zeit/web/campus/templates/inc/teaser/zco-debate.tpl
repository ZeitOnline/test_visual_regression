{%- extends "zeit.web.campus:templates/inc/shared/debate.tpl" -%}

{% block kicker %}{{ teaser.teaserSupertitle or teaser.supertitle }}{% endblock %}
{% block title %}{{ teaser.teaserTitle or teaser.title }}{% endblock %}
{% block text %}{{ teaser.teaserText }}{% endblock %}

{% block wrapper_start %}
    <article class="teaser-debate" data-unique-id="{{ teaser.uniqueId }}" data-meetrics="{{ area.kind }}" data-clicktracking="{{ area.kind }}">
{% endblock %}

{% block wrapper_end %}
    </article>
{% endblock %}
