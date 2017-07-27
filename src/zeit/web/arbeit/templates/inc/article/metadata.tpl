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
            <div class="summary" itemprop="description">
                {{ view.subtitle }}
            </div>
            {%- set byline = view.context | get_byline('main') %}
            {% if byline | length -%}
            <div class="byline" data-ct-row="author">
                {% include 'zeit.web.core:templates/inc/meta/byline.html' %}
            </div>
            {% endif -%}
            <div class="{{ 'metadata' | with_mods('zplus') if self.zplus_badge() else 'metadata' }}">
                {% include "zeit.web.core:templates/inc/article/metadata.tpl" %}
                {% block zplus_badge %}{% endblock %}
            </div>
        {% endblock %}
    {% endif %}
</div>
