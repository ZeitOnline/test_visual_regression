{% extends "zeit.web.site:templates/inc/article/metadata.tpl" %}

{% block modifier %}article__item--has-badge{% endblock %}
{% block intro %}
    <div class="article__zplus">
        <div class="article__intro">
            <div class="summary" itemprop="description">
                {{ view.subtitle }}
             </div>
            {%- set byline = view.context | get_byline('main') %}
            {% if byline | length -%}
                <div class="byline">
                    {% include 'zeit.web.core:templates/inc/meta/byline.html' %}
                </div>
            {% endif -%}
            <div class="metadata">
                {% include "zeit.web.core:templates/inc/article/metadata.tpl" %}
            </div>
        </div>
    {% include "zeit.web.site:templates/inc/article/zplus-badge.tpl" %}
    </div>
{% endblock %}

