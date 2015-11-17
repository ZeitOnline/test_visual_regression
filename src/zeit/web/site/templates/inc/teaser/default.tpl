{% import 'zeit.web.site:templates/macros/layout_macro.tpl' as lama %}
{% import 'zeit.web.site:templates/macros/centerpage_macro.tpl' as cp %}

{% block teaser %}
<article class="{% block layout %}{{ layout | default('default') }}{% endblock %} {% block teaser_modifier %}{% endblock %}{% if module.visible_mobile == False %} mobile-hidden{% endif %}" data-unique-id="{{ teaser.uniqueId }}"{% block meetrics %} data-meetrics="{{ area.kind }}"{% endblock %} data-clicktracking="{{ area.kind }}" {% block teaser_attributes %}{% endblock %}>

    {% block teaser_label %}{% endblock %}
    {% block teaser_media_position_before_title %}{% endblock %}

    <div class="{{ self.layout() }}__container">

        {% block teaser_journalistic_format %}
            {% if teaser.serie and not teaser.serie.column %}
                <div class="{{ self.layout() }}__series-label">Serie: {{ teaser.serie.serienname }}</div>
            {% elif teaser.blog %}
                <div class="blog-format">
                    <span class="blog-format__marker">Blog</span>
                    <span class="blog-format__name">{{ teaser.blog.name }}</span>
                </div>
            {% endif %}
        {% endblock teaser_journalistic_format %}

        {% block teaser_heading %}
            <h2 class="{{ self.layout() }}__heading {% block teaser_heading_modifier %}{% endblock %}">
                {% block teaser_link %}
                <a class="{{ self.layout() }}__combined-link"
                   title="{{ teaser.teaserSupertitle or teaser.supertitle }} - {{ teaser.teaserTitle or teaser.title }}"
                   href="{{ teaser | create_url }}">
                    {%- block teaser_kicker %}
                    {% set kicker_class = '%s__kicker' | format(self.layout()) %}
                    {% set is_zmo_teaser = provides(teaser, 'zeit.magazin.interfaces.IZMOContent') %}
                    {% set is_zmo_parquet = area.referenced_cp and provides(area.referenced_cp, 'zeit.magazin.interfaces.IZMOContent') %}
                    {% set is_zett_content = provides(teaser, 'zeit.content.link.interfaces.ILink') and teaser.url.startswith('http://ze.tt') %}
                    {% set is_zett_parquet = (area.kind == 'zett')%}
                    <span class="{{ kicker_class | with_mods(
                        journalistic_format,
                        area.kind if area.kind == 'spektrum',
                        'zmo' if is_zmo_teaser and not is_zmo_parquet,
                        'zmo-parquet' if is_zmo_parquet,
                        'zett' if is_zett_content and not is_zett_parquet,
                        'zett-parquet' if is_zett_parquet
                        )}}">
                        {% block kicker_logo scoped -%}
                        {%- if is_zmo_teaser and not is_zmo_parquet %}
                            {{ lama.use_svg_icon('logo-zmo-zm', kicker_class + '-logo--zmo svg-symbol--hide-ie', request) }}
                        {%- elif is_zett_content and not is_zett_parquet %}
                            {{ lama.use_svg_icon('logo-zett-small', kicker_class + '-logo--zett svg-symbol--hide-ie', request) }}
                        {%- endif %}
                        {%- endblock -%}
                        {{ teaser.teaserSupertitle or teaser.supertitle }}</span>
                    {%- if teaser.teaserSupertitle or teaser.supertitle %}<span class="visually-hidden">:</span>{% endif %}
                    {% endblock %}
                    {% block teaser_title %}
                    <span class="{{ self.layout() }}__title">{{ teaser.teaserTitle or teaser.title }}</span>
                    {% endblock %}
                    {% block teaser_product %}
                       {# Use this for short teaser #}
                    {% endblock %}
                </a>
                {% endblock teaser_link %}
            </h2>
        {% endblock teaser_heading %}

        {% block teaser_media_position_after_title %}{% endblock %}

        {% block teaser_container %}
            {% block teaser_text %}
                {# TODO: Extract teaser-length text snippet from articles that don't have a teaser text. #}
                <p class="{{ self.layout() }}__text">{{ teaser.teaserText }}</p>
            {% endblock %}
            {% block teaser_metadata_default %}
            <div class="{{ self.layout() }}__metadata">
                {% block teaser_byline %}
                    <span class="{{ self.layout() }}__byline">
                        {%- set byline = teaser | get_byline -%}
                        {%- include 'zeit.web.site:templates/inc/meta/byline.tpl' -%}
                    </span>
                {% endblock %}
                {% block teaser_datetime %}
                    {% if not view.is_advertorial %}
                        {{ cp.include_teaser_datetime(teaser, self.layout(), area.kind) }}
                    {% endif %}
                {% endblock %}
                {% block teaser_commentcount %}
                    {% set comments = view.comment_counts[teaser.uniqueId] %}
                    {% if comments %}
                        {% set comments_string = comments | pluralize('Keine Kommentare', '{} Kommentar', '{} Kommentare') %}
                        <a class="{{ self.layout() }}__commentcount js-update-commentcount" href="{{ teaser | create_url }}#comments" title="Kommentare anzeigen">{{ comments_string }}</a>
                    {% endif %}
                {% endblock %}
            </div>
            {% endblock %}
        {% endblock %}
    </div>

    {% block teaser_media_position_after_container %}{% endblock %}

</article>
{% if view.is_hp and region_loop and region_loop.index == 1 and area_loop.index == 1 and loop.index == 1 %}
    {{ lama.adplace(view.banner(3), view, mobile=True) }}
{% endif %}
{% endblock %}
