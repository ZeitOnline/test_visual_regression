{% import 'zeit.web.site:templates/macros/layout_macro.tpl' as lama %}

{% if view.featuretoggle_articlelineage and view.lineage %}
<div class="article-lineage js-fix-position">
    {% set predecessor, successor = view.lineage %}
    <a href="{{ predecessor.uniqueId | create_url }}" class="article-lineage__link article-lineage__link--prev" data-id="articlebottom.article-lineage.prev..{{ predecessor.title | format_webtrekk }}">
        {# TODO: use Icon as background image via CSS ? #}
        {# Rotation of the icon is not done via CSS because of IE8.
           We use 2 different SVGs instead. Could be improved after IE8 is gone. #}
        {{ lama.use_svg_icon('arrow-articlelineage-left', 'article-lineage__link-icon article-lineage__link-icon--prev', request) }}
        <span class="article-lineage__link-text article-lineage__link-text--prev">
            <span class="article-lineage__link-kicker">{% if predecessor.uniqueId == 'http://xml.zeit.de/index' %}ZEIT ONLINE{% else %}Voriger Artikel{% endif %}</span>
            <span class="article-lineage__link-title">{{ predecessor.title | hide_none }}</span>
        </span>
    </a>
    <a href="{{ successor.uniqueId | create_url }}" class="article-lineage__link article-lineage__link--next"data-id="articlebottom.article-lineage.next..{{ successor.title | format_webtrekk }}">
        {# TODO: use Icon as background image via CSS ? #}
        {{ lama.use_svg_icon('arrow-articlelineage-right', 'article-lineage__link-icon article-lineage__link-icon--next', request) }}
        <span class="article-lineage__link-text article-lineage__link-text--next">
            <span class="article-lineage__link-kicker">{% if successor.uniqueId == 'http://xml.zeit.de/index' %}ZEIT ONLINE{% else %}Nächster Artikel{% endif %}</span>
            <span class="article-lineage__link-title">{{ successor.title | hide_none }}</span>
        </span>
    </a>
</div>
{% endif %}
