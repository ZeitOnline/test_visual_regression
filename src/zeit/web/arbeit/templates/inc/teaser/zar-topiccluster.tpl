{%- extends "zeit.web.arbeit:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-topiccluster{% endblock %}

{% block teaser_kicker %}{% endblock %}
{% block teaser_container %}{% endblock %}

{% block teaser_title %}{{- teaser.teaserSupertitle or teaser.supertitle -}}{% endblock %}
