{% import 'zeit.web.site:templates/macros/layout_macro.tpl' as lama %}

{% if toggles('article_lineage') and view.lineage %}
<div class="article-lineage js-fix-position">
    {% set predecessor, successor = view.lineage %}
    <a href="{{ predecessor.uniqueId | create_url }}" class="al-link al-link--prev" data-id="articlebottom.article-lineage.prev..{{ predecessor.title | format_webtrekk }}">
        {# TODO: use Icon as background image via CSS ? #}
        {# Rotation of the icon is not done via CSS because of IE8.
           We use 2 different SVGs instead. Could be improved after IE8 is gone. #}
        {{ lama.use_svg_icon('arrow-articlelineage-left', 'al-link__icon al-link__icon--prev', view.package) }}
        <span class="al-text al-text--prev {% if predecessor.supertitle %}al-text--has-supertitle{% endif %}">
            <span class="al-text__kicker">{% if predecessor.uniqueId == 'http://xml.zeit.de/index' %}ZEIT ONLINE{% else %}Voriger Artikel{% endif %}</span>
            {% if predecessor.supertitle %}<span class="al-text__supertitle">{{ predecessor.supertitle }}</span>{% endif %}
            <span class="al-text__title">{{ predecessor.title }}</span>
        </span>
    </a>
    <a href="{{ successor.uniqueId | create_url }}" class="al-link al-link--next" data-id="articlebottom.article-lineage.next..{{ successor.title | format_webtrekk }}">
        {# TODO: use Icon as background image via CSS ? #}
        {{ lama.use_svg_icon('arrow-articlelineage-right', 'al-link__icon al-link__icon--next', view.package) }}
        <span class="al-text al-text--next {% if successor.supertitle %}al-text--has-supertitle{% endif %}">
            <span class="al-text__kicker">{% if successor.uniqueId == 'http://xml.zeit.de/index' %}ZEIT ONLINE{% else %}Nächster Artikel{% endif %}</span>
            {% if successor.supertitle %}<span class="al-text__supertitle">{{ successor.supertitle }}</span>{% endif %}
            <span class="al-text__title">{{ successor.title }}</span>
        </span>
    </a>
</div>
{% endif %}
