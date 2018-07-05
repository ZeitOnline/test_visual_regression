{% set headertag = 'div' if view.pagination and view.pagination.current > 1 and view.current_page.teaser else 'h1' %}
<{{ headertag }} class="article-heading">
    <span class="article-heading__kicker">
        {{- view.supertitle -}}
    </span>
    {%- if view.title %}<span class="visually-hidden">: </span>{% endif -%}
    <span class="article-heading__title">
        <span class="{{ 'article-heading__title--underlined' if view.is_advertorial else 'article-heading__title--underlined-skip' }}">{{- view.title -}}</span>
    </span>
</{{ headertag }}>
