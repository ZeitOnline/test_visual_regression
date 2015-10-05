{% import 'zeit.web.site:templates/macros/layout_macro.tpl' as lama %}

<div class="article-lineage js-fix-position">
    {% set predecessor, successor = view.lineage %}
    <a href="{{ predecessor.uniqueId | create_url }}" class="article-lineage__link article-lineage__link--prev">
        {# TODO: use Icon as background image via CSS ? #}
        {{ lama.use_svg_icon('arrow', 'article-lineage__link-icon article-lineage__link-icon--prev', request) }}
        <span class="article-lineage__link-text article-lineage__link-text--prev">
            <span class="article-lineage__link-kicker">{% if successor.uniqueId == 'http://xml.zeit.de/index' %}ZEIT ONLINE{% else %}Voriger Artikel{% endif %}</span>
            <span class="article-lineage__link-title">{{ predecessor.title | hide_none }}</span>
        </span>
    </a>
    <a href="{{ successor.uniqueId | create_url }}" class="article-lineage__link article-lineage__link--next">
        {# TODO: use Icon as background image via CSS ? #}
        {{ lama.use_svg_icon('arrow', 'article-lineage__link-icon article-lineage__link-icon--next', request) }}
        <span class="article-lineage__link-text article-lineage__link-text--next">
            <span class="article-lineage__link-kicker">{% if successor.uniqueId == 'http://xml.zeit.de/index' %}ZEIT ONLINE{% else %}Nächster Artikel{% endif %}</span>
            <span class="article-lineage__link-title">{{ successor.title | hide_none }}</span>
        </span>
    </a>
</div>
