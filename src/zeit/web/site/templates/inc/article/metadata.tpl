<div class="article__item">
{% if view.pagination and view.pagination.current > 1 %}
    <div class="article__page-teaser">
        Seite {{ view.pagination.current }}/{{ view.pagination.total }}
        {%- if view.current_page.teaser -%}
            : <h1>{{ view.current_page.teaser }}</h1>
        {% endif %}
    </div>
{% else %}
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
{% endif %}
</div>
