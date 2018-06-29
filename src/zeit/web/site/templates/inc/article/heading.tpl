<div class="article__item {% block modifier %}{% endblock %}">
    {% set headertag = 'div' if view.pagination and view.pagination.current > 1 and view.current_page.teaser else 'h1' %}
    <{{ headertag }} class="article-heading">
        <span class="article-heading__kicker">
            {%- if view.context is column -%}
                {{- view.serie + ' / ' -}}
            {%- endif -%}
            {{- view.supertitle -}}
        </span>
        {%- if view.title %}<span class="visually-hidden">: </span>{% endif -%}
        <span class="article-heading__title">
            {{- view.title -}}
        </span>
    </{{ headertag }}>
</div>
