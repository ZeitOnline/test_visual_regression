{% set headertag = 'div' if view.pagination and view.pagination.current > 1 and view.current_page.teaser else 'h1' %}
<{{ headertag }} class="article-heading" itemprop="headline">
    <span class="article-heading__kicker">
        {%- if view.serie -%}
            {{- view.serie + ' / ' -}}
        {%- endif -%}
        {{- view.supertitle -}}
    </span>
    {%- if view.title %}<span class="visually-hidden">: </span>{% endif -%}
    <span class="article-heading__title">
        <span class="article-heading__title--underlined">{{- view.title -}}</span>
    </span>
</{{ headertag }}>
