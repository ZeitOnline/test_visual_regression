{% extends "zeit.web.site:templates/inc/article/metadata.tpl" %}

{% block modifier %}article__item--has-badge article__item--wide{% endblock %}
{% block intro %}
    <div class="article__zplus">
        <div class="article__intro">
            {{ super() }}
        </div>
    {% include "zeit.web.site:templates/inc/article/zplus-badge.tpl" %}
    </div>
{% endblock %}
