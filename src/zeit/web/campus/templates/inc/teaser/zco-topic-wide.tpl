{%- extends "zeit.web.campus:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-topic-wide{% endblock %}
{% block teaser_datetime %}{% endblock %}

{% block teaser_content %}
    <div class="{{ self.layout() }}__content">
        {{ super() }}
    </div>
{% endblock %}
