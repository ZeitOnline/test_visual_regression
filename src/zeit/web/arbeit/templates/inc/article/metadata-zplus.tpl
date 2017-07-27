{% extends "zeit.web.arbeit:templates/inc/article/metadata.tpl" %}
{% block zplus_badge %}
    {% if view.zplus_label and view.zplus_label.zplus and view.page_nr == 1 %}
        {% include "zeit.web.core:templates/inc/article/zplus-badge.html" %}
    {% endif %}
{% endblock %}
