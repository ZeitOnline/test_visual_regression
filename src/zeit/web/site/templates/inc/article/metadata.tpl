{% import 'zeit.web.site:templates/macros/layout_macro.tpl' as lama %}

<div class="article__item {% if view.context is zplus_content_article %}article__item--has-badge{% endif %}">
    {% if view.pagination and view.pagination.current > 1 %}
        <div class="article__page-teaser">
            Seite {{ view.pagination.current }}/{{ view.pagination.total }}
            {%- if view.current_page.teaser -%}
                : <h1>{{ view.current_page.teaser }}</h1>
            {% endif %}
        </div>
    {% else %}
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
        {% if view.context is zplus_content_article %}
            {% include "zeit.web.site:templates/inc/article/zplus-badge.tpl" %}
        {% endif %}
    {% endif %}
</div>

