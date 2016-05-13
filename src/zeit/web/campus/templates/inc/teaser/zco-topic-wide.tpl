{%- extends "zeit.web.campus:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-topic-wide{% endblock %}

{% block teaser_content %}
    {%- set ref_cp = area.referenced_cp %}
    {%- set topic_supertitle = area.supertitle or ref_cp.teaserSupertitle or ref_cp.supertitle %}
    {%- set readmore_url = area.read_more_url | create_url %}
    {%- if not readmore_url and ref_cp is not none %}
        {%- set readmore_url = ref_cp.uniqueId | create_url %}
    {%- endif %}

    {%- if readmore_url -%}
        <a class="{{ self.layout() }}__topic-button" title="{{ topic_supertitle }} - {{ area.title }}" href="{{ readmore_url }}">
            {{- topic_supertitle -}}
        </a>
    {%- endif -%}

    {{ super() }}
{% endblock %}
