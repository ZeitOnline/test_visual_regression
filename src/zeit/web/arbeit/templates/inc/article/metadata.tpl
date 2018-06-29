<div class="article__item {% block modifier %}{% endblock %}">
    {% if view.pagination and view.pagination.current > 1 %}
        <div class="article__page-teaser">
            Seite {{ view.pagination.current }}/{{ view.pagination.total }}
            {%- if view.current_page.teaser -%}
                : <h1 class="article__page-teaser-title">{{ view.current_page.teaser }}</h1>
            {% endif %}
        </div>
    {% else %}
        {% block intro %}
            <div class="summary">
                {{ view.subtitle }}
            </div>
            {% if not byline_already_rendered %}
                {%- set byline = view.context | get_byline('main') %}
                {% if byline | length -%}
                    <div class="byline" data-ct-row="author">
                        {% include 'zeit.web.core:templates/inc/meta/byline.html' %}
                    </div>
                {% endif -%}
            {% endif %}
            <div class="metadata">
                {% include "zeit.web.core:templates/inc/article/metadata.tpl" %}
            </div>

            {% if view.zplus_label and view.zplus_label.zplus %}
                {% include "zeit.web.core:templates/inc/article/zplus-badge.html" %}
            {% endif %}
        {% endblock %}
    {% endif %}
</div>
