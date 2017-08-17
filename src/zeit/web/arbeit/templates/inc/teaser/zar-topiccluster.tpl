{%- extends "zeit.web.arbeit:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-topiccluster{% endblock %}

{% block teaser_kicker %}{% endblock %}
{% block teaser_container %}{% endblock %}

{% block teaser_title %}{{- teaser.teaserSupertitle or teaser.supertitle -}}{% endblock %}

{# We want to avoid teaser__container, so we set the heading as the only content. #}
{% block teaser_allcontent %}
    {% block teaser_heading %}
        {{ super() }}
    {% endblock %}
{% endblock %}
